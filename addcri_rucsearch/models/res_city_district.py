from odoo import fields, models, api

class L10nPeResCityDistrict(models.Model):
    _inherit = 'l10n_pe.res.city.district'
    
    def name_get(self):
        res = []
        for district in self:
            if district.city_id:
                display_name = '%s (%s)' % (district.name, district.city_id.name)
            else:
                display_name = district.name
            res.append((district.id, display_name))
        return res