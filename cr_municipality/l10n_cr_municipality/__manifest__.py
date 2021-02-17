{
    "name": "l10n_cr_municipality",
    "version": "14.0.0.1.0",
    "author": "HomebrewSoft",
    "website": "https://homebrewsoft.dev",
    "license": "LGPL-3",
    "depends": [
        "account",
        "l10n_cr_territories",
        "sale",
        "uom",
    ],
    "data": [
        # security
        "security/ir.model.access.csv",
        # data
        "data/ir_sequence.xml",
        "data/product_product.xml",
        "data/l10n_cr_identification.xml",
        "data/l10n_cr_patent_type.xml",
        "data/l10n_cr.ciiu.csv",
        "data/patent_certificate_paperformat.xml",
        # reports
        "reports/patent_certificate.xml",
        "reports/patent_pos.xml",
        "reports/patent_sign.xml",
        # reports patents
	    'reports/patent_reports.xml',
        'reports/patent_deny_licor_template.xml',
        'reports/patent_aprobb_licor_template.xml',
        'reports/patent_aprobb_mcr_template.xml',
        'reports/patent_deny_mcr_template.xml',
        # views
        "views/menus.xml",
        "views/l10n_cr_land.xml",
        "views/l10n_cr_patent_approve_wizard.xml",
        "views/l10n_cr_patent_reject_wizard.xml",
        "views/l10n_cr_patent.xml",
        "views/res_config_settings.xml",
        "views/res_partner.xml",
        "views/sale_order.xml",
    ],
}
