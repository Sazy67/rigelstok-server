# Windows Server 2012 Deployment Script
# Bu scripti Administrator olarak çalıştırın

Write-Host "Rigelstok Windows Server 2012 Deployment" -ForegroundColor Green

# 1. wfastcgi kurulumu
Write-Host "wfastcgi kuruluyor..." -ForegroundColor Yellow
pip install wfastcgi

# 2. wfastcgi IIS'e kaydet
Write-Host "wfastcgi IIS'e kaydediliyor..." -ForegroundColor Yellow
wfastcgi-enable

# 3. IIS Application Pool oluştur
Write-Host "Application Pool oluşturuluyor..." -ForegroundColor Yellow
Import-Module WebAdministration
New-WebAppPool -Name "RigelstokPool" -Force
Set-ItemProperty -Path "IIS:\AppPools\RigelstokPool" -Name "processModel.identityType" -Value "ApplicationPoolIdentity"
Set-ItemProperty -Path "IIS:\AppPools\RigelstokPool" -Name "enable32BitAppOnWin64" -Value $false

# 4. Web Site oluştur
Write-Host "Web Site oluşturuluyor..." -ForegroundColor Yellow
New-Website -Name "Rigelstok" -PhysicalPath "C:\inetpub\wwwroot\rigelstok" -Port 80 -ApplicationPool "RigelstokPool" -Force

# 5. Gerekli klasörleri oluştur
Write-Host "Klasörler oluşturuluyor..." -ForegroundColor Yellow
New-Item -ItemType Directory -Path "C:\inetpub\wwwroot\rigelstok\uploads" -Force
New-Item -ItemType Directory -Path "C:\inetpub\wwwroot\rigelstok\logs" -Force

# 6. Dosya izinlerini ayarla
Write-Host "Dosya izinleri ayarlanıyor..." -ForegroundColor Yellow
$acl = Get-Acl "C:\inetpub\wwwroot\rigelstok"
$accessRule = New-Object System.Security.AccessControl.FileSystemAccessRule("IIS_IUSRS","FullControl","ContainerInherit,ObjectInherit","None","Allow")
$acl.SetAccessRule($accessRule)
Set-Acl "C:\inetpub\wwwroot\rigelstok" $acl

# 7. Firewall kuralı ekle (isteğe bağlı)
Write-Host "Firewall kuralı ekleniyor..." -ForegroundColor Yellow
New-NetFirewallRule -DisplayName "Rigelstok HTTP" -Direction Inbound -Protocol TCP -LocalPort 80 -Action Allow

Write-Host "Deployment tamamlandı!" -ForegroundColor Green
Write-Host "Web sitesine http://localhost veya http://[server-ip] adresinden erişebilirsiniz" -ForegroundColor Cyan

# 8. Servisleri yeniden başlat
Write-Host "IIS yeniden başlatılıyor..." -ForegroundColor Yellow
iisreset

Write-Host "Kurulum tamamlandı! Web sitesini test edin." -ForegroundColor Green