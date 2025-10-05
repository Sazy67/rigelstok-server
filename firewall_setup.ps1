# Rigelstok Flask Uygulaması için Güvenlik Duvarı Ayarları
# Bu scripti Administrator olarak çalıştırın

Write-Host "Rigelstok Güvenlik Duvarı Ayarları Başlatılıyor..." -ForegroundColor Green

# Mevcut kuralları kontrol et ve sil
Write-Host "Mevcut kurallar kontrol ediliyor..." -ForegroundColor Yellow
$existingRules = Get-NetFirewallRule -DisplayName "*Rigelstok*" -ErrorAction SilentlyContinue
if ($existingRules) {
    Write-Host "Mevcut Rigelstok kuralları siliniyor..." -ForegroundColor Yellow
    Remove-NetFirewallRule -DisplayName "*Rigelstok*"
}

# Port 5001 için Inbound kuralı
Write-Host "Port 5001 için Inbound kuralı ekleniyor..." -ForegroundColor Cyan
New-NetFirewallRule -DisplayName "Rigelstok Flask App - Port 5001" `
                    -Direction Inbound `
                    -Protocol TCP `
                    -LocalPort 5001 `
                    -Action Allow `
                    -Profile Domain,Private,Public `
                    -Description "Rigelstok Flask uygulaması için 5001 portu"

# Port 5001 için Outbound kuralı
Write-Host "Port 5001 için Outbound kuralı ekleniyor..." -ForegroundColor Cyan
New-NetFirewallRule -DisplayName "Rigelstok Flask App - Port 5001 Outbound" `
                    -Direction Outbound `
                    -Protocol TCP `
                    -LocalPort 5001 `
                    -Action Allow `
                    -Profile Domain,Private,Public `
                    -Description "Rigelstok Flask uygulaması için 5001 portu outbound"

# HTTP Port 80 için kural (isteğe bağlı)
Write-Host "HTTP Port 80 için kural ekleniyor (isteğe bağlı)..." -ForegroundColor Cyan
New-NetFirewallRule -DisplayName "Rigelstok HTTP - Port 80" `
                    -Direction Inbound `
                    -Protocol TCP `
                    -LocalPort 80 `
                    -Action Allow `
                    -Profile Domain,Private,Public `
                    -Description "Rigelstok HTTP için 80 portu"

# HTTPS Port 443 için kural (isteğe bağlı)
Write-Host "HTTPS Port 443 için kural ekleniyor (isteğe bağlı)..." -ForegroundColor Cyan
New-NetFirewallRule -DisplayName "Rigelstok HTTPS - Port 443" `
                    -Direction Inbound `
                    -Protocol TCP `
                    -LocalPort 443 `
                    -Action Allow `
                    -Profile Domain,Private,Public `
                    -Description "Rigelstok HTTPS için 443 portu"

# Python.exe için program kuralı
Write-Host "Python.exe için program kuralı ekleniyor..." -ForegroundColor Cyan
$pythonPath = (Get-Command python -ErrorAction SilentlyContinue).Source
if ($pythonPath) {
    New-NetFirewallRule -DisplayName "Rigelstok Python Application" `
                        -Direction Inbound `
                        -Program $pythonPath `
                        -Action Allow `
                        -Profile Domain,Private,Public `
                        -Description "Rigelstok Python uygulaması için program kuralı"
    Write-Host "Python yolu: $pythonPath" -ForegroundColor Gray
}

# Kuralları listele
Write-Host "`nOluşturulan güvenlik duvarı kuralları:" -ForegroundColor Green
Get-NetFirewallRule -DisplayName "*Rigelstok*" | Select-Object DisplayName, Direction, Action, Enabled | Format-Table -AutoSize

# Güvenlik duvarı durumunu kontrol et
Write-Host "`nGüvenlik duvarı profil durumları:" -ForegroundColor Green
Get-NetFirewallProfile | Select-Object Name, Enabled | Format-Table -AutoSize

Write-Host "`n✅ Güvenlik duvarı ayarları tamamlandı!" -ForegroundColor Green
Write-Host "🌐 Uygulamanıza şu adreslerden erişebilirsiniz:" -ForegroundColor Cyan
Write-Host "   - Yerel: http://localhost:5001" -ForegroundColor White
Write-Host "   - Ağ: http://[bilgisayar-ip]:5001" -ForegroundColor White
Write-Host "`n⚠️  Not: Ağ erişimi için bilgisayarınızın IP adresini kullanın" -ForegroundColor Yellow

# IP adresi bilgilerini göster
Write-Host "`n🔍 Mevcut IP adresleri:" -ForegroundColor Green
Get-NetIPAddress -AddressFamily IPv4 | Where-Object {$_.InterfaceAlias -notlike "*Loopback*"} | Select-Object IPAddress, InterfaceAlias | Format-Table -AutoSize