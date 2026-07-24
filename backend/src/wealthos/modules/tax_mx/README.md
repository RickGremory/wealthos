# Tax MX (Sprint 4.4)

Mexico tax foundation module: ISR/IVA configuration, classification, monthly workpaper, and operational estimates integrated with core `taxes` periods.

## Catalog import

Bundled catalogs live in `catalogs/data/catalogs-v1.json`. Load into `mx_tax_catalog_entries` with:

```bash
cd backend
python -m wealthos.modules.tax_mx.catalogs.import_catalog
```

`GET /organizations/{id}/taxes/mx/catalogs` auto-seeds v1 when the catalog table is empty.

## API (under `/api/v1/organizations/{organization_id}/taxes/mx`)

- Configuration: `POST/GET/PATCH .../configuration`
- Catalogs: `GET .../catalogs`
- Category mappings: `POST/GET/PATCH .../category-mappings`
- Classification: `POST .../transactions/{transaction_id}/classification`
- Tax details: `POST .../transactions/{transaction_id}/tax-details`
- Unclassified: `GET .../transactions/unclassified`
- Calculate: `POST .../periods/{period_id}/calculate`
- Workpaper: `GET .../periods/{period_id}/workpaper`
- Summary: `GET .../summary`
- Staleness: `GET .../periods/{period_id}/staleness`

Roles: config admin/owner; classify/calculate member+; reads include viewer.
