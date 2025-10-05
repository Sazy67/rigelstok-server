/**
 * Ürün Autocomplete Bileşeni
 * Kullanım: initProductAutocomplete('input-id', callback)
 */

class ProductAutocomplete {
    constructor(inputId, options = {}) {
        this.input = document.getElementById(inputId);
        this.options = {
            minLength: 2,
            delay: 300,
            maxResults: 10,
            onSelect: options.onSelect || function() {},
            placeholder: options.placeholder || 'Ürün ara...',
            ...options
        };
        
        this.dropdown = null;
        this.currentFocus = -1;
        this.searchTimeout = null;
        this.isOpen = false;
        
        this.init();
    }
    
    init() {
        if (!this.input) return;
        
        // Input placeholder
        this.input.placeholder = this.options.placeholder;
        
        // Dropdown container oluştur
        this.createDropdown();
        
        // Event listener'ları ekle
        this.input.addEventListener('input', (e) => this.handleInput(e));
        this.input.addEventListener('keydown', (e) => this.handleKeydown(e));
        this.input.addEventListener('focus', (e) => this.handleFocus(e));
        this.input.addEventListener('blur', (e) => this.handleBlur(e));
        
        // Document click - dropdown'ı kapat
        document.addEventListener('click', (e) => {
            if (!this.input.contains(e.target) && !this.dropdown.contains(e.target)) {
                this.hideDropdown();
            }
        });
    }
    
    createDropdown() {
        this.dropdown = document.createElement('div');
        this.dropdown.className = 'autocomplete-dropdown';
        this.dropdown.style.cssText = `
            position: absolute;
            top: 100%;
            left: 0;
            right: 0;
            background: white;
            border: 1px solid #ddd;
            border-top: none;
            border-radius: 0 0 4px 4px;
            max-height: 300px;
            overflow-y: auto;
            z-index: 1000;
            display: none;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        `;
        
        // Input'un parent'ına relative position ekle
        const parent = this.input.parentElement;
        if (getComputedStyle(parent).position === 'static') {
            parent.style.position = 'relative';
        }
        
        parent.appendChild(this.dropdown);
    }
    
    handleInput(e) {
        const value = e.target.value.trim();
        
        // Timeout'u temizle
        if (this.searchTimeout) {
            clearTimeout(this.searchTimeout);
        }
        
        if (value.length < this.options.minLength) {
            this.hideDropdown();
            return;
        }
        
        // Debounce search
        this.searchTimeout = setTimeout(() => {
            this.search(value);
        }, this.options.delay);
    }
    
    handleKeydown(e) {
        if (!this.isOpen) return;
        
        const items = this.dropdown.querySelectorAll('.autocomplete-item');
        
        switch (e.key) {
            case 'ArrowDown':
                e.preventDefault();
                this.currentFocus = Math.min(this.currentFocus + 1, items.length - 1);
                this.updateFocus(items);
                break;
                
            case 'ArrowUp':
                e.preventDefault();
                this.currentFocus = Math.max(this.currentFocus - 1, -1);
                this.updateFocus(items);
                break;
                
            case 'Enter':
                e.preventDefault();
                if (this.currentFocus >= 0 && items[this.currentFocus]) {
                    this.selectItem(items[this.currentFocus]);
                }
                break;
                
            case 'Escape':
                this.hideDropdown();
                break;
        }
    }
    
    handleFocus(e) {
        const value = e.target.value.trim();
        if (value.length >= this.options.minLength) {
            this.search(value);
        }
    }
    
    handleBlur(e) {
        // Kısa bir delay ile kapat (click event'i için)
        setTimeout(() => {
            if (!this.dropdown.matches(':hover')) {
                this.hideDropdown();
            }
        }, 150);
    }
    
    async search(query) {
        try {
            const response = await fetch(`/api/search-products?q=${encodeURIComponent(query)}`);
            const products = await response.json();
            
            this.showResults(products);
        } catch (error) {
            console.error('Autocomplete search error:', error);
            this.hideDropdown();
        }
    }
    
    showResults(products) {
        if (products.length === 0) {
            this.hideDropdown();
            return;
        }
        
        this.dropdown.innerHTML = '';
        this.currentFocus = -1;
        
        products.forEach((product, index) => {
            const item = document.createElement('div');
            item.className = 'autocomplete-item';
            item.style.cssText = `
                padding: 10px 12px;
                cursor: pointer;
                border-bottom: 1px solid #f0f0f0;
                transition: background-color 0.2s;
            `;
            
            item.innerHTML = `
                <div style="font-weight: 500; color: #333;">${this.highlightMatch(product.display_text, this.input.value)}</div>
                <div style="font-size: 0.85em; color: #666; margin-top: 2px;">${product.detail_text}</div>
            `;
            
            // Hover effect
            item.addEventListener('mouseenter', () => {
                this.currentFocus = index;
                this.updateFocus([item]);
            });
            
            item.addEventListener('click', () => {
                this.selectItem(item, product);
            });
            
            // Data attribute'u ekle
            item.dataset.product = JSON.stringify(product);
            
            this.dropdown.appendChild(item);
        });
        
        this.showDropdown();
    }
    
    highlightMatch(text, query) {
        if (!query) return text;
        
        const regex = new RegExp(`(${query.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')})`, 'gi');
        return text.replace(regex, '<strong style="background-color: #fff3cd;">$1</strong>');
    }
    
    updateFocus(items) {
        items.forEach((item, index) => {
            if (index === this.currentFocus) {
                item.style.backgroundColor = '#e3f2fd';
            } else {
                item.style.backgroundColor = '';
            }
        });
    }
    
    selectItem(item, product = null) {
        if (!product) {
            product = JSON.parse(item.dataset.product);
        }
        
        // Input'a ürün kodunu yaz
        this.input.value = product.urun_kodu;
        
        // Callback'i çağır
        this.options.onSelect(product, this.input);
        
        this.hideDropdown();
        
        // Custom event dispatch et
        this.input.dispatchEvent(new CustomEvent('productSelected', {
            detail: product
        }));
    }
    
    showDropdown() {
        this.dropdown.style.display = 'block';
        this.isOpen = true;
    }
    
    hideDropdown() {
        this.dropdown.style.display = 'none';
        this.isOpen = false;
        this.currentFocus = -1;
    }
    
    destroy() {
        if (this.dropdown && this.dropdown.parentElement) {
            this.dropdown.parentElement.removeChild(this.dropdown);
        }
    }
}

// Global function for easy initialization
function initProductAutocomplete(inputId, options = {}) {
    return new ProductAutocomplete(inputId, options);
}

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ProductAutocomplete;
}