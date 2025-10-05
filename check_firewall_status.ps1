# Güvenlik Duvarı ve Ağ Bağlantısı Kontrol Scripti

Write-Host "🔍 Rigelstok Güvenlik Duvarı ve Ağ Durumu Kontrolü" -ForegroundColor Green

# 1. Güvenlik duvarı profil durumları
Write-Host "`n1. Güvenlik Duvarı Profil Durumları:" -ForegroundColor Cyan
Get-NetFirewallProfile | Select-Object Name, Enabled, DefaultInboundAction, DefaultOutboundAction | Format-Table -AutoSize

# 2. Rigelstok ile ilgili kurallar
Write-Host "`n2. Rigelstok Güvenlik Duvarı Kuralları:" -ForegroundColor Cyan
$rigelstokRules = Get-NetFirewallRule -DisplayName "*Rigelstok*" -ErrorAction SilentlyContinue
if ($rigelstokRules) {
    $rigelstokRules | Select-Object DisplayName, Direction, Action, Enabled | Format-Table -AutoSize
} else {
    Write-Host "   ❌ Rigelstok için güvenlik duvarı kuralı bulunamadı!" -ForegroundColor Red
}

# 3. Port 5001 için kurallar
Write-Host "`n3. Port 5001 Kuralları:" -ForegroundColor Cyan
$port5001Rules = Get-NetFirewallPortFilter | Where-Object {$_.LocalPort -eq 5001}
if ($port5001Rules) {
    foreach ($rule in $port5001Rules) {
        $firewallRule = Get-NetFirewallRule -AssociatedNetFirewallPortFilter $rule
        Write-Host "   ✅ $($firewallRule.DisplayName) - $($firewallRule.Direction) - $($firewallRule.Action)" -ForegroundColor Green
    }
} else {
    Write-Host "   ❌ Port 5001 için kural bulunamadı!" -ForegroundColor Red
}

# 4. Aktif ağ bağlantıları
Write-Host "`n4. Aktif Ağ Bağlantıları:" -ForegroundColor Cyan
Get-NetIPAddress -AddressFamily IPv4 | Where-Object {$_.InterfaceAlias -notlike "*Loopback*" -and $_.PrefixOrigin -eq "Dhcp"} | 
    Select-Object IPAddress, InterfaceAlias | Format-Table -AutoSize

# 5. Port 5001 dinleme durumu
Write-Host "`n5. Port 5001 Dinleme Durumu:" -ForegroundColor Cyan
$listening = Get-NetTCPConnection -LocalPort 5001 -ErrorAction SilentlyContinue
if ($listening) {
    $listening | Select-Object LocalAddress, LocalPort, State, OwningProcess | Format-Table -AutoSize
    Write-Host "   ✅ Port 5001 aktif olarak dinleniyor!" -ForegroundColor Green
} else {
    Write-Host "   ⚠️  Port 5001 dinlenmiyor. Flask uygulaması çalışıyor mu?" -ForegroundColor Yellow
}

# 6. Bağlantı testi
Write-Host "`n6. Yerel Bağlantı Testi:" -ForegroundColor Cyan
try {
    $response = Invoke-WebRequest -Uri "http://localhost:5001/health" -TimeoutSec 5 -ErrorAction Stop
    Write-Host "   ✅ Uygulama sağlıklı çalışıyor! (Status: $($response.StatusCode))" -ForegroundColor Green
} catch {
    Write-Host "   ❌ Uygulamaya bağlanılamıyor: $($_.Exception.Message)" -ForegroundColor Red
}

# 7. Öneriler
Write-Host "`n📋 Öneriler:" -ForegroundColor Yellow
Write-Host "   • Flask uygulamasını çalıştırmak için: python app.py" -ForegroundColor White
Write-Host "   • Güvenlik duvarı kuralları eklemek için: .\firewall_setup.ps1 (Administrator olarak)" -ForegroundColor White
Write-Host "   • Ağ erişimi için bilgisayar IP'si: http://[ip-adresi]:5001" -ForegroundColor White
Write-Host "   • Yerel erişim: http://localhost:5001" -ForegroundColor White