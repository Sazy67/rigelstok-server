"""
Performans İyileştirme Modülü
Performance Optimization Module
"""

import time
import functools
from datetime import datetime, timedelta
from threading import RLock

class SimpleCache:
    """Basit bellek içi cache sistemi"""
    
    def __init__(self, default_timeout=300):  # 5 dakika
        self.cache = {}
        self.timeouts = {}
        self.default_timeout = default_timeout
        self.lock = RLock()
    
    def get(self, key):
        """Cache'den veri al"""
        with self.lock:
            if key in self.cache:
                # Timeout kontrolü
                if self.timeouts[key] > datetime.now():
                    return self.cache[key]
                else:
                    # Süresi dolmuş, temizle
                    del self.cache[key]
                    del self.timeouts[key]
            return None
    
    def set(self, key, value, timeout=None):
        """Cache'e veri ekle"""
        with self.lock:
            if timeout is None:
                timeout = self.default_timeout
            
            self.cache[key] = value
            self.timeouts[key] = datetime.now() + timedelta(seconds=timeout)
    
    def delete(self, key):
        """Cache'den veri sil"""
        with self.lock:
            if key in self.cache:
                del self.cache[key]
                del self.timeouts[key]
    
    def clear(self):
        """Cache'i temizle"""
        with self.lock:
            self.cache.clear()
            self.timeouts.clear()
    
    def cleanup(self):
        """Süresi dolmuş verileri temizle"""
        with self.lock:
            now = datetime.now()
            expired_keys = [
                key for key, timeout in self.timeouts.items()
                if timeout <= now
            ]
            
            for key in expired_keys:
                del self.cache[key]
                del self.timeouts[key]

# Global cache instance
app_cache = SimpleCache()

def cached(timeout=300, key_func=None):
    """Cache decorator'ı"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Cache key oluştur
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                cache_key = f"{func.__name__}_{hash(str(args) + str(kwargs))}"
            
            # Cache'den kontrol et
            cached_result = app_cache.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Cache'de yok, hesapla ve kaydet
            result = func(*args, **kwargs)
            app_cache.set(cache_key, result, timeout)
            return result
        
        return wrapper
    return decorator

def timing_decorator(func):
    """İşlem süresini ölç"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        
        execution_time = end_time - start_time
        print(f"{func.__name__} işlemi {execution_time:.4f} saniyede tamamlandı")
        
        return result
    return wrapper

class PerformanceMonitor:
    """Performans izleme sınıfı"""
    
    def __init__(self):
        self.metrics = {}
        self.lock = RLock()
    
    def record_timing(self, operation, duration):
        """İşlem süresini kaydet"""
        with self.lock:
            if operation not in self.metrics:
                self.metrics[operation] = []
            
            self.metrics[operation].append({
                'duration': duration,
                'timestamp': datetime.now()
            })
            
            # Son 100 kayıtı tut
            if len(self.metrics[operation]) > 100:
                self.metrics[operation] = self.metrics[operation][-100:]
    
    def get_average_time(self, operation):
        """Ortalama işlem süresini al"""
        with self.lock:
            if operation not in self.metrics or not self.metrics[operation]:
                return 0
            
            durations = [m['duration'] for m in self.metrics[operation]]
            return sum(durations) / len(durations)
    
    def get_stats(self):
        """Tüm istatistikleri al"""
        with self.lock:
            stats = {}
            for operation, records in self.metrics.items():
                if records:
                    durations = [r['duration'] for r in records]
                    stats[operation] = {
                        'count': len(durations),
                        'average': sum(durations) / len(durations),
                        'min': min(durations),
                        'max': max(durations),
                        'last_24h': len([
                            r for r in records
                            if r['timestamp'] > datetime.now() - timedelta(hours=24)
                        ])
                    }
            return stats

# Global performance monitor
perf_monitor = PerformanceMonitor()

def monitor_performance(operation_name):
    """Performans izleme decorator'ı"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                duration = time.time() - start_time
                perf_monitor.record_timing(operation_name, duration)
        return wrapper
    return decorator

# Veritabanı optimizasyonu fonksiyonları
def optimize_database_queries():
    """Veritabanı sorgularını optimize et"""
    optimizations = [
        "PRAGMA journal_mode=WAL;",
        "PRAGMA synchronous=NORMAL;",
        "PRAGMA cache_size=10000;",
        "PRAGMA temp_store=MEMORY;",
        "PRAGMA mmap_size=268435456;",  # 256MB
    ]
    
    return optimizations

def create_database_indexes():
    """Performans için gerekli indeksleri oluştur"""
    indexes = [
        "CREATE INDEX IF NOT EXISTS idx_stoklar_urun_kodu_konum ON stoklar(urun_kodu, konum);",
        "CREATE INDEX IF NOT EXISTS idx_stoklar_adet ON stoklar(adet);",
        "CREATE INDEX IF NOT EXISTS idx_stoklar_updated_at ON stoklar(updated_at);",
        "CREATE INDEX IF NOT EXISTS idx_hareketler_tarih_urun ON stok_hareketleri(tarih, urun_kodu);",
        "CREATE INDEX IF NOT EXISTS idx_hareketler_hareket_tipi ON stok_hareketleri(hareket_tipi);",
        "CREATE INDEX IF NOT EXISTS idx_kullanicilar_kullanici_adi ON kullanicilar(kullanici_adi);",
        "CREATE INDEX IF NOT EXISTS idx_kullanicilar_son_giris ON kullanicilar(son_giris);",
    ]
    
    return indexes

# Cache key fonksiyonları
def stock_list_cache_key(page, per_page, search, location, color):
    """Stok listesi cache anahtarı"""
    return f"stock_list_{page}_{per_page}_{hash(search or '')}_{hash(location or '')}_{hash(color or '')}"

def dashboard_stats_cache_key():
    """Dashboard istatistikleri cache anahtarı"""
    return "dashboard_stats"

def stock_report_cache_key(search, location_filter, color_filter, sort_by, sort_order):
    """Stok raporu cache anahtarı"""
    return f"stock_report_{hash(search or '')}_{hash(location_filter or '')}_{hash(color_filter or '')}_{sort_by}_{sort_order}"

# Performans test fonksiyonları
def benchmark_function(func, *args, **kwargs):
    """Fonksiyon performansını test et"""
    import statistics
    
    times = []
    for _ in range(10):
        start = time.time()
        func(*args, **kwargs)
        times.append(time.time() - start)
    
    return {
        'average': statistics.mean(times),
        'median': statistics.median(times),
        'min': min(times),
        'max': max(times),
        'std_dev': statistics.stdev(times) if len(times) > 1 else 0
    }

class DatabaseConnectionPool:
    """Basit veritabanı bağlantı havuzu"""
    
    def __init__(self, max_connections=10):
        self.max_connections = max_connections
        self.connections = []
        self.used_connections = set()
        self.lock = RLock()
    
    def get_connection(self):
        """Havuzdan bağlantı al"""
        with self.lock:
            # Kullanılmayan bağlantı var mı?
            for conn in self.connections:
                if conn not in self.used_connections:
                    self.used_connections.add(conn)
                    return conn
            
            # Yeni bağlantı oluştur (maksimum sınırı kontrol et)
            if len(self.connections) < self.max_connections:
                import sqlite3
                conn = sqlite3.connect('stok_takip_dev.db', check_same_thread=False)
                conn.row_factory = sqlite3.Row
                self.connections.append(conn)
                self.used_connections.add(conn)
                return conn
            
            # Bağlantı havuzu dolu
            raise Exception("Bağlantı havuzu dolu, lütfen bekleyin")
    
    def release_connection(self, conn):
        """Bağlantıyı havuza geri ver"""
        with self.lock:
            if conn in self.used_connections:
                self.used_connections.remove(conn)
    
    def close_all(self):
        """Tüm bağlantıları kapat"""
        with self.lock:
            for conn in self.connections:
                conn.close()
            self.connections.clear()
            self.used_connections.clear()

# Global connection pool
db_pool = DatabaseConnectionPool()

# Cache temizleme görevleri
def schedule_cache_cleanup():
    """Cache temizleme görevi planla"""
    import threading
    
    def cleanup_task():
        while True:
            time.sleep(300)  # 5 dakikada bir
            app_cache.cleanup()
    
    cleanup_thread = threading.Thread(target=cleanup_task, daemon=True)
    cleanup_thread.start()