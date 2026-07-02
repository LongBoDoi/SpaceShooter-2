# Generates Resources/Images/Auras.png - a 2-cell (128px) sheet of soft white
# aura sprites, tinted per power-up in-game and drawn around the ship.
#   cell 0 = RING (bubble)  -> SHIELD
#   cell 1 = GLOW (radial)  -> SPEED / RAPID
Add-Type -AssemblyName System.Drawing

$cell = 128
$sheet = New-Object System.Drawing.Bitmap(($cell * 2), $cell)
$g = [System.Drawing.Graphics]::FromImage($sheet)
$g.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::AntiAlias
$g.Clear([System.Drawing.Color]::FromArgb(0, 0, 0, 0))

# cell 0: soft ring (bubble) - concentric outlines with alpha falloff around r=52
$cx = 64
for ($d = -9; $d -le 9; $d++) {
    $alpha = [int](210 * (1 - [Math]::Abs($d) / 9.5))
    if ($alpha -lt 0) { $alpha = 0 }
    $pen = New-Object System.Drawing.Pen([System.Drawing.Color]::FromArgb($alpha, 255, 255, 255), 2)
    $r = 50 + $d
    $g.DrawEllipse($pen, ($cx - $r), (64 - $r), (2 * $r), (2 * $r))
    $pen.Dispose()
}

# cell 1: radial glow - bright centre fading to transparent edge
$ox = $cell
$path = New-Object System.Drawing.Drawing2D.GraphicsPath
$path.AddEllipse($ox, 0, $cell, $cell)
$pgb = New-Object System.Drawing.Drawing2D.PathGradientBrush($path)
$pgb.CenterPoint = New-Object System.Drawing.PointF(($ox + 64), 64)
$pgb.CenterColor = [System.Drawing.Color]::FromArgb(200, 255, 255, 255)
$pgb.SurroundColors = @([System.Drawing.Color]::FromArgb(0, 255, 255, 255))
$g.FillPath($pgb, $path)
$pgb.Dispose()
$path.Dispose()

$g.Dispose()
$dst = Join-Path (Resolve-Path (Join-Path $PSScriptRoot "..\Resources\Images")).Path "Auras.png"
$sheet.Save($dst, [System.Drawing.Imaging.ImageFormat]::Png)
$sheet.Dispose()
Write-Host "Generated Auras.png (256x128, 2 cells)"
