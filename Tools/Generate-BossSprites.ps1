<#
    Generate-BossSprites.ps1
    -------------------------
    Procedurally generates placeholder sprite art for the Boss Battle system
    using .NET GDI+ (System.Drawing). No Python / Pillow required.

    Output: Resources/Images/boss/
        BossMarauder.png      256x256  variant 1 (red, swept-wing assault)
        BossSentinel.png      256x256  variant 2 (cyan, hex interceptor)
        BossDreadnought.png   256x256  variant 3 (purple, heavy gunship)
        BossProjectiles.png   256x64   2 rows x 8 cols, 32px pulse animation
        BossWarning.png       1024x128 telegraph banner
        BossHealthBar.png     1200x70  gradient fill (clip from left)
        BossHealthFrame.png   1200x70  bar frame / chrome

    All bosses face DOWN (toward the player at the bottom of the screen).
    Re-run any time to regenerate; tweak the palettes/points below to taste.
#>

Add-Type -AssemblyName System.Drawing

$ScriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$OutDir = Join-Path (Split-Path -Parent $ScriptRoot) 'Resources\Images\boss'
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null

# ---------- helpers --------------------------------------------------------
function New-Canvas([int]$w, [int]$h) {
    $bmp = New-Object System.Drawing.Bitmap($w, $h, [System.Drawing.Imaging.PixelFormat]::Format32bppArgb)
    $g = [System.Drawing.Graphics]::FromImage($bmp)
    $g.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::AntiAlias
    $g.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
    $g.Clear([System.Drawing.Color]::FromArgb(0,0,0,0))
    return @($bmp, $g)
}
function C([int]$a,[int]$r,[int]$g,[int]$b){ [System.Drawing.Color]::FromArgb($a,$r,$g,$b) }
function P([double]$x,[double]$y){ New-Object System.Drawing.PointF([single]$x,[single]$y) }

# Radial glow centered at (cx,cy) radius r: bright center fading to transparent.
function Add-Glow($g, [double]$cx, [double]$cy, [double]$r, $center, $edge) {
    $path = New-Object System.Drawing.Drawing2D.GraphicsPath
    $path.AddEllipse([single]($cx-$r), [single]($cy-$r), [single]($r*2), [single]($r*2))
    $pgb = New-Object System.Drawing.Drawing2D.PathGradientBrush($path)
    $pgb.CenterPoint = P $cx $cy
    $pgb.CenterColor = $center
    $pgb.SurroundColors = @($edge)
    $g.FillPath($pgb, $path)
    $pgb.Dispose(); $path.Dispose()
}

# Build a vertically-symmetric polygon from right-half points (x increasing
# away from centre line cx). First point should be the nose, last the tail.
function Mirror-Points([double]$cx, [array]$right) {
    $pts = New-Object System.Collections.Generic.List[System.Drawing.PointF]
    foreach ($p in $right) { $pts.Add((P $p[0] $p[1])) }
    for ($i = $right.Count - 2; $i -ge 1; $i--) {
        $p = $right[$i]
        $pts.Add((P (2*$cx - $p[0]) $p[1]))
    }
    return ,$pts.ToArray()
}

# Fill + outline a hull polygon with a vertical metallic gradient.
function Draw-Hull($g, [System.Drawing.PointF[]]$poly, $top, $bottom, $outline) {
    $rect = New-Object System.Drawing.RectangleF(0,0,256,256)
    $lgb = New-Object System.Drawing.Drawing2D.LinearGradientBrush($rect, $top, $bottom, 90.0)
    $g.FillPolygon($lgb, $poly)
    $pen = New-Object System.Drawing.Pen($outline, 2.5)
    $pen.LineJoin = [System.Drawing.Drawing2D.LineJoin]::Round
    $g.DrawPolygon($pen, $poly)
    $lgb.Dispose(); $pen.Dispose()
}

function Save-Bmp($bmp, [string]$name) {
    $path = Join-Path $OutDir $name
    $bmp.Save($path, [System.Drawing.Imaging.ImageFormat]::Png)
    Write-Host ("  wrote {0}  ({1}x{2})" -f $name, $bmp.Width, $bmp.Height)
}

# ---------- a generic boss drawer ------------------------------------------
# palette = @{ Top; Bottom; Outline; Glow; Core } ; right = right-half hull pts
function Draw-Boss($name, $right, $palette, $turrets, $coreR) {
    $c = New-Canvas 256 256
    $bmp = $c[0]; $g = $c[1]
    $cx = 128.0

    # engine glow at the rear (top of canvas)
    Add-Glow $g $cx 40 70 (C 150 ($palette.Glow.R) ($palette.Glow.G) ($palette.Glow.B)) (C 0 0 0 0)

    $poly = Mirror-Points $cx $right
    Draw-Hull $g $poly $palette.Top $palette.Bottom $palette.Outline

    # panel highlight: a smaller, brighter inner polygon
    $inner = foreach ($p in $right) { ,@(($cx + ($p[0]-$cx)*0.55), ($p[1]*0.92 + 12)) }
    $ipoly = Mirror-Points $cx $inner
    $hb = New-Object System.Drawing.SolidBrush(C 45 255 255 255)
    $g.FillPolygon($hb, $ipoly); $hb.Dispose()

    # turrets (dark mounts + barrels pointing down)
    foreach ($t in $turrets) {
        $tx = $t[0]; $ty = $t[1]; $tr = $t[2]
        $mb = New-Object System.Drawing.SolidBrush(C 255 28 30 40)
        $g.FillEllipse($mb, [single]($tx-$tr), [single]($ty-$tr), [single]($tr*2), [single]($tr*2))
        $g.FillEllipse($mb, [single](2*$cx-$tx-$tr), [single]($ty-$tr), [single]($tr*2), [single]($tr*2))
        $bp = New-Object System.Drawing.Pen((C 255 18 20 28), [single]($tr*0.7))
        $g.DrawLine($bp, [single]$tx, [single]$ty, [single]$tx, [single]($ty+$tr*2.4))
        $g.DrawLine($bp, [single](2*$cx-$tx), [single]$ty, [single](2*$cx-$tx), [single]($ty+$tr*2.4))
        $mb.Dispose(); $bp.Dispose()
    }

    # glowing core / cockpit
    Add-Glow $g $cx 150 ($coreR*2.2) (C 200 ($palette.Core.R) ($palette.Core.G) ($palette.Core.B)) (C 0 0 0 0)
    $cb = New-Object System.Drawing.SolidBrush(C 255 250 250 255)
    $g.FillEllipse($cb, [single]($cx-$coreR*0.45), [single](150-$coreR*0.45), [single]($coreR*0.9), [single]($coreR*0.9))
    $cb.Dispose()

    Save-Bmp $bmp $name
    $g.Dispose(); $bmp.Dispose()
}

Write-Host "Generating boss sprites into $OutDir"

# --- Variant 1: Marauder (red/orange, broad swept wings) -------------------
Draw-Boss 'BossMarauder.png' @(
    @(128,242), @(150,206), @(206,168), @(246,118), @(202,116),
    @(174,150), @(184,70), @(150,46), @(128,58)
) @{
    Top    = (C 255 255 120 70);  Bottom = (C 255 120 24 18)
    Outline= (C 255 255 200 140); Glow   = (C 0 255 120 40)
    Core   = (C 0 255 220 120)
} @( ,@(206,150,11) ) 26

# --- Variant 2: Sentinel (cyan/teal, hexagonal interceptor) -----------------
Draw-Boss 'BossSentinel.png' @(
    @(128,232), @(176,196), @(202,140), @(188,92), @(150,68), @(128,60)
) @{
    Top    = (C 255 120 240 255); Bottom = (C 255 20 110 150)
    Outline= (C 255 180 250 255); Glow   = (C 0 60 230 255)
    Core   = (C 0 120 255 230)
} @( ,@(176,150,10) ) 24

# --- Variant 3: Dreadnought (purple, heavy multi-turret gunship) ------------
Draw-Boss 'BossDreadnought.png' @(
    @(128,238), @(170,214), @(232,176), @(238,120), @(214,118),
    @(196,150), @(206,64), @(150,40), @(128,54)
) @{
    Top    = (C 255 200 130 255); Bottom = (C 255 84 28 130)
    Outline= (C 255 225 190 255); Glow   = (C 0 170 60 255)
    Core   = (C 0 200 120 255)
} @( @(214,150,12), @(168,186,9) ) 28

# ---------- Boss projectiles: 2 rows x 8 cols, 32px pulse ------------------
# Row 0 = red plasma, Row 1 = violet void. Columns = animation frames.
function Draw-Projectiles {
    $cell = 32; $cols = 8; $rows = 2
    $c = New-Canvas ($cell*$cols) ($cell*$rows)
    $bmp = $c[0]; $g = $c[1]
    $palettes = @(
        @{ Center = (C 255 255 245 210); Mid = (C 230 255 90 50);  Edge = (C 0 180 20 0) },
        @{ Center = (C 255 245 220 255); Mid = (C 230 180 70 255); Edge = (C 0 90 0 140) }
    )
    for ($r = 0; $r -lt $rows; $r++) {
        for ($i = 0; $i -lt $cols; $i++) {
            $cx = $i*$cell + $cell/2.0
            $cy = $r*$cell + $cell/2.0
            # pulse 0..1..0 across the 8 frames
            $t = [math]::Sin($i / [double]($cols-1) * [math]::PI)
            $rad = 7 + 6*$t
            $pal = $palettes[$r]
            Add-Glow $g $cx $cy ($rad+5) $pal.Mid $pal.Edge
            $cb = New-Object System.Drawing.SolidBrush($pal.Center)
            $g.FillEllipse($cb, [single]($cx-$rad*0.5), [single]($cy-$rad*0.5), [single]($rad), [single]($rad))
            $cb.Dispose()
        }
    }
    Save-Bmp $bmp 'BossProjectiles.png'
    $g.Dispose(); $bmp.Dispose()
}
Draw-Projectiles

# ---------- Warning banner -------------------------------------------------
function Draw-Warning {
    $w = 1024; $h = 128
    $c = New-Canvas $w $h
    $bmp = $c[0]; $g = $c[1]
    # translucent dark slab
    $bg = New-Object System.Drawing.SolidBrush(C 200 12 6 10)
    $g.FillRectangle($bg, 0, 24, $w, $h-48); $bg.Dispose()
    # hazard stripes top & bottom
    $yellow = C 255 255 196 0
    $sp = New-Object System.Drawing.Pen($yellow, 10)
    for ($x = -120; $x -lt $w; $x += 34) {
        $g.DrawLine($sp, [single]$x, 24, [single]($x+24), 44)
        $g.DrawLine($sp, [single]$x, ($h-44), [single]($x+24), ($h-24))
    }
    $sp.Dispose()
    # text
    $sf = New-Object System.Drawing.StringFormat
    $sf.Alignment = [System.Drawing.StringAlignment]::Center
    $sf.LineAlignment = [System.Drawing.StringAlignment]::Center
    $rect = New-Object System.Drawing.RectangleF(0, 16, $w, ($h-32))
    $f1 = New-Object System.Drawing.Font('Arial', 40, [System.Drawing.FontStyle]::Bold)
    $tb = New-Object System.Drawing.SolidBrush($yellow)
    $g.DrawString("WARNING  -  BOSS APPROACHING", $f1, $tb, $rect, $sf)
    $f1.Dispose(); $tb.Dispose(); $sf.Dispose()
    Save-Bmp $bmp 'BossWarning.png'
    $g.Dispose(); $bmp.Dispose()
}
Draw-Warning

# ---------- Health bar + frame (match existing 1200x70) --------------------
function Draw-HealthAssets {
    $w = 1200; $h = 70
    # fill bar: red->orange->yellow left to right; game clips width from left
    $c = New-Canvas $w $h
    $bmp = $c[0]; $g = $c[1]
    $rect = New-Object System.Drawing.RectangleF(0,0,$w,$h)
    $cb = New-Object System.Drawing.Drawing2D.ColorBlend(3)
    $cb.Colors = @((C 255 220 30 30), (C 255 255 140 20), (C 255 255 230 60))
    $cb.Positions = @(0.0, 0.6, 1.0)
    $lgb = New-Object System.Drawing.Drawing2D.LinearGradientBrush($rect, (C 0 0 0 0), (C 0 0 0 0), 0.0)
    $lgb.InterpolationColors = $cb
    $g.FillRectangle($lgb, 0,0,$w,$h)
    # gloss highlight on top half
    $gl = New-Object System.Drawing.SolidBrush(C 60 255 255 255)
    $g.FillRectangle($gl, 0,0,$w,[int]($h*0.4)); $gl.Dispose()
    $lgb.Dispose()
    Save-Bmp $bmp 'BossHealthBar.png'
    $g.Dispose(); $bmp.Dispose()

    # frame: dark chrome border with notches
    $c2 = New-Canvas $w $h
    $bmp2 = $c2[0]; $g2 = $c2[1]
    $bgb = New-Object System.Drawing.SolidBrush(C 120 10 12 18)
    $g2.FillRectangle($bgb, 0,0,$w,$h); $bgb.Dispose()
    $pen = New-Object System.Drawing.Pen((C 255 200 210 230), 5)
    $g2.DrawRectangle($pen, 3,3,$w-7,$h-7); $pen.Dispose()
    $np = New-Object System.Drawing.Pen((C 160 200 210 230), 2)
    for ($x = 120; $x -lt $w; $x += 120) { $g2.DrawLine($np, [single]$x, 6, [single]$x, [single]($h-6)) }
    $np.Dispose()
    Save-Bmp $bmp2 'BossHealthFrame.png'
    $g2.Dispose(); $bmp2.Dispose()
}
Draw-HealthAssets

Write-Host "Done."
