# Generates Resources/Images/PowerUps.png - a 5-cell (64px) sprite sheet of
# power-up icons, using pure .NET GDI+ (no Python needed), matching the boss
# placeholder-art workflow.
#   cell 0 = POWER  (orange, up-arrow)   -> bullet upgrade
#   cell 1 = SPEED  (cyan, lightning)    -> temporary speed boost (timed)
#   cell 2 = REPAIR (green, plus)        -> +1 life
#   cell 3 = SHIELD (purple, shield)     -> temporary invulnerability (timed)
#   cell 4 = RAPID  (red, bars)          -> temporary rapid fire (timed)
#   cell 5 = HEART  (pink, heart)        -> extra life (can exceed base 3, up to max)
Add-Type -AssemblyName System.Drawing

$cell = 64
$sheet = New-Object System.Drawing.Bitmap(($cell * 6), $cell)
$g = [System.Drawing.Graphics]::FromImage($sheet)
$g.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::AntiAlias
$g.Clear([System.Drawing.Color]::FromArgb(0, 0, 0, 0))

$defs = @(
    @{ fill = @(255,140,20);  edge = @(255,205,90)  },   # POWER  orange
    @{ fill = @(50,190,255);  edge = @(160,230,255) },   # SPEED  cyan
    @{ fill = @(60,215,90);   edge = @(165,255,180) },   # REPAIR green
    @{ fill = @(170,110,255); edge = @(210,175,255) },   # SHIELD purple
    @{ fill = @(255,80,80);   edge = @(255,160,160) },   # RAPID  red
    @{ fill = @(255,95,150);  edge = @(255,170,200) }    # HEART  pink
)

for ($i = 0; $i -lt 6; $i++) {
    $ox = $i * $cell
    $d = $defs[$i]
    $fill = [System.Drawing.Color]::FromArgb(255, $d.fill[0], $d.fill[1], $d.fill[2])
    $edge = [System.Drawing.Color]::FromArgb(255, $d.edge[0], $d.edge[1], $d.edge[2])

    # orb: filled circle + bright rim
    $rect = New-Object System.Drawing.Rectangle(($ox + 8), 8, 48, 48)
    $brush = New-Object System.Drawing.SolidBrush($fill)
    $g.FillEllipse($brush, $rect)
    $pen = New-Object System.Drawing.Pen($edge, 4)
    $g.DrawEllipse($pen, $rect)

    $white = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::White)

    if ($i -eq 0) {
        # up arrow (power)
        $pts = @(
            (New-Object System.Drawing.Point(($ox + 32), 18)),
            (New-Object System.Drawing.Point(($ox + 47), 40)),
            (New-Object System.Drawing.Point(($ox + 37), 40)),
            (New-Object System.Drawing.Point(($ox + 37), 48)),
            (New-Object System.Drawing.Point(($ox + 27), 48)),
            (New-Object System.Drawing.Point(($ox + 27), 40)),
            (New-Object System.Drawing.Point(($ox + 17), 40))
        )
        $g.FillPolygon($white, $pts)
    } elseif ($i -eq 1) {
        # lightning bolt (speed)
        $pts = @(
            (New-Object System.Drawing.Point(($ox + 37), 16)),
            (New-Object System.Drawing.Point(($ox + 22), 36)),
            (New-Object System.Drawing.Point(($ox + 31), 36)),
            (New-Object System.Drawing.Point(($ox + 27), 50)),
            (New-Object System.Drawing.Point(($ox + 44), 30)),
            (New-Object System.Drawing.Point(($ox + 34), 30))
        )
        $g.FillPolygon($white, $pts)
    } elseif ($i -eq 2) {
        # plus (repair)
        $g.FillRectangle($white, ($ox + 28), 18, 8, 28)
        $g.FillRectangle($white, ($ox + 18), 28, 28, 8)
    } elseif ($i -eq 3) {
        # shield (badge shape)
        $pts = @(
            (New-Object System.Drawing.Point(($ox + 32), 16)),
            (New-Object System.Drawing.Point(($ox + 46), 22)),
            (New-Object System.Drawing.Point(($ox + 46), 34)),
            (New-Object System.Drawing.Point(($ox + 32), 50)),
            (New-Object System.Drawing.Point(($ox + 18), 34)),
            (New-Object System.Drawing.Point(($ox + 18), 22))
        )
        $g.FillPolygon($white, $pts)
    } elseif ($i -eq 4) {
        # three bars (rapid fire)
        $g.FillRectangle($white, ($ox + 22), 21, 5, 22)
        $g.FillRectangle($white, ($ox + 30), 21, 5, 22)
        $g.FillRectangle($white, ($ox + 38), 21, 5, 22)
    } else {
        # heart (two lobes + point)
        $g.FillEllipse($white, ($ox + 18), 20, 15, 15)
        $g.FillEllipse($white, ($ox + 31), 20, 15, 15)
        $pts = @(
            (New-Object System.Drawing.Point(($ox + 18), 29)),
            (New-Object System.Drawing.Point(($ox + 46), 29)),
            (New-Object System.Drawing.Point(($ox + 32), 48))
        )
        $g.FillPolygon($white, $pts)
    }
}

$g.Dispose()
$dst = Join-Path $PSScriptRoot "..\Resources\Images\PowerUps.png"
$sheet.Save((Resolve-Path (Split-Path $dst)).Path + "\PowerUps.png", [System.Drawing.Imaging.ImageFormat]::Png)
$sheet.Dispose()
Write-Host "Generated PowerUps.png (384x64, 6 cells)"
