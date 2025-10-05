"""
Rezervasyon işlemleri için API endpoint'leri
"""

from flask import Blueprint, request, jsonify, current_app
from utils.database import get_db_connection, get_urun_rezervasyon_notu, save_urun_rezervasyon_notu, delete_urun_rezervasyon_notu
import logging

logger = logging.getLogger(__name__)

reservation_bp = Blueprint('reservation', __name__)

@reservation_bp.route('/api/rezervasyon-notu-kaydet', methods=['POST'])
def api_rezervasyon_notu_kaydet():
    """Rezervasyon notu kaydetme API - artık ürün bazlı"""
    try:
        data = request.get_json()
        logger.info(f"Received reservation note save request: {data}")
        
        urun_kodu = data.get('urun_kodu', '').strip()
        renk = data.get('renk', '').strip() if data.get('renk') else None
        note = data.get('note', '').strip()
        
        # Gelen verileri daha detaylı logla
        logger.info(f"Processing reservation note - Product: '{urun_kodu}', Color: '{renk}', Note: '{note}'")
        logger.info(f"Color value type: {type(renk)}, Color value repr: {repr(renk)}")
        
        if not urun_kodu:
            return jsonify({'success': False, 'message': 'Ürün kodu gereklidir'})
        
        # Log before saving
        logger.info(f"About to call save_urun_rezervasyon_notu for {urun_kodu}")
        
        # Stok kaydı olup olmadığını kontrol etmeden direkt olarak notu kaydet
        result = save_urun_rezervasyon_notu(urun_kodu, renk, note)
        
        # Log after saving
        logger.info(f"save_urun_rezervasyon_notu returned: {result}")
        
        # Verify the note was actually saved by retrieving it
        saved_note = get_urun_rezervasyon_notu(urun_kodu, renk)
        logger.info(f"Verification - Retrieved note for {urun_kodu}: '{saved_note}'")
        
        if result:
            logger.info(f"Successfully saved reservation note for {urun_kodu}")
            return jsonify({
                'success': True,
                'message': 'Rezervasyon notu başarıyla kaydedildi',
                'saved_note': saved_note
            })
        else:
            logger.error(f"Failed to save reservation note for {urun_kodu}")
            return jsonify({
                'success': False,
                'message': 'Rezervasyon notu kaydedilemedi'
            })
        
    except Exception as e:
        logger.error(f"Rezervasyon notu kaydetme API error: {str(e)}")
        logger.error(f"Traceback: ", exc_info=True)
        return jsonify({'success': False, 'message': f'Hata: {str(e)}'})

@reservation_bp.route('/api/rezervasyon-notu-getir')
def api_rezervasyon_notu_getir():
    """Ürün bazlı rezervasyon notu getirme API"""
    try:
        urun_kodu = request.args.get('urun_kodu', '').strip()
        renk = request.args.get('renk', '').strip()
        
        if not urun_kodu:
            return jsonify({'success': False, 'message': 'Ürün kodu gereklidir'})
        
        # Yeni tablodan getir
        rezervasyon_notu = get_urun_rezervasyon_notu(urun_kodu, renk if renk else None)
        
        return jsonify({
            'success': True,
            'rezervasyon_notu': rezervasyon_notu
        })
        
    except Exception as e:
        logger.error(f"Rezervasyon notu getirme API error: {str(e)}")
        return jsonify({'success': False, 'message': f'Hata: {str(e)}'})

@reservation_bp.route('/api/rezervasyon-notu-sil', methods=['POST'])
def api_rezervasyon_notu_sil():
    """Ürün bazlı rezervasyon notu silme API"""
    try:
        data = request.get_json()
        urun_kodu = data.get('urun_kodu', '').strip()
        renk = data.get('renk', '').strip() if data.get('renk') else None
        
        if not urun_kodu:
            return jsonify({'success': False, 'message': 'Ürün kodu gereklidir'})
        
        # Not olup olmadığını kontrol et
        rezervasyon_notu = get_urun_rezervasyon_notu(urun_kodu, renk)
        if rezervasyon_notu is None:
            # Not yoksa başarılı olarak dön (idempotent)
            return jsonify({
                'success': True,
                'message': 'Rezervasyon notu silindi'
            })
        
        # Notu sil
        result = delete_urun_rezervasyon_notu(urun_kodu, renk)
        
        if result:
            return jsonify({
                'success': True,
                'message': 'Rezervasyon notu başarıyla silindi'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Rezervasyon notu silinemedi'
            })
        
    except Exception as e:
        logger.error(f"Rezervasyon notu silme API error: {str(e)}")
        return jsonify({'success': False, 'message': f'Hata: {str(e)}'})
