---
name: gtm-catalog
description: "Manage Meta product catalogs and connect them to pixels for catalog-based conversion tracking"
argument-hint: "[list|create|get|connect|delete] [name or id] [--vertical <type>]"
---

# Meta Product Catalog Command

You manage Meta product catalogs via the official **`meta ads` CLI**. Catalogs hold product inventory for Advantage+ catalog ads, shopping, and commerce. Once created, a catalog can be connected to a Meta Pixel for product-level conversion tracking.

Full CLI reference: `skills/meta-ads/rules/ads-cli.md` (§9 Catalogs, §8 Datasets).

## Phase 0: Pre-Flight

1. Read `.gtm/config.json` and load `.env.gtm`.
   - If `.gtm/config.json` does not exist, tell the user: "GTM Command Center is not set up. Run `/gtm-setup` first." Then STOP.
2. Verify the CLI:
   ```bash
   command -v meta >/dev/null 2>&1 || { echo "meta CLI not installed. Run /gtm-setup."; exit 1; }
   meta auth status
   [ $? -eq 3 ] && { echo "ACCESS_TOKEN invalid/expired. Refresh in Business Manager."; exit 3; }
   ```
3. Parse `$ARGUMENTS` to determine the action:
   - `list` (default if no args) → §1
   - `create <name> [--vertical <type>]` → §2
   - `get <catalog_id>` → §3
   - `connect <catalog_id> --pixel <pixel_id>` → §4
   - `delete <catalog_id> [--force]` → §5

## §1. List Catalogs

```bash
meta ads catalog list --output json | jq -r '.[] | "\(.id)\t\(.name)\t\(.vertical)\t\(.product_count) products\t\(.feed_count) feeds"'
```

Present as a table:

```
ID                  Name                Vertical    Products    Feeds
1234567890123       Main Catalog        commerce    0           0
1234567890456       Hotel Inventory     hotels      230         1
```

If the user has no catalogs, suggest: "Run `/gtm-catalog create <name>` to create one."

## §2. Create Catalog

Inputs:
- **Name** (required) — passed as the first argument or asked interactively.
- **Vertical** (optional, defaults to `commerce`) — one of: `adoptable_pets, commerce, destinations, flights, generic, home_listings, hotels, local_service_businesses, offer_items, offline_commerce, transactable_items, vehicles`.

If the user did not specify `--vertical`, infer a reasonable default from `.gtm/config.json` and the detected stack:

| Project signal | Suggested vertical |
|---|---|
| Stripe products with prices, ecom-style stack (Shopify/Woo/etc.) | `commerce` |
| Booking-related routes / hotels keywords / Airbnb-style | `hotels` |
| Travel/flight booking | `flights` or `destinations` |
| Real-estate listings | `home_listings` |
| Job board / classifieds | `offer_items` |
| Anything else | `commerce` (safe default) |

Confirm with the user before creating: "Create catalog '<name>' with vertical '<vertical>'? (y/n)"

```bash
CATALOG_ID=$(meta ads catalog create \
  --name "$NAME" \
  --vertical "$VERTICAL" \
  --output json | jq -r '.id')

[ -z "$CATALOG_ID" ] || [ "$CATALOG_ID" = "null" ] && { echo "Catalog creation failed"; exit 4; }
echo "Created catalog: $CATALOG_ID"
```

After creation, **offer to connect** the catalog to the configured pixel (read from `.gtm/config.json` `meta.pixel_id`):

> "Connect this catalog to your pixel `<pixel_id>` for product-level conversion tracking? (y/n)"

If yes, proceed to §4 with the just-created `$CATALOG_ID`.

Save the catalog reference to `.gtm/config.json` under `meta.catalog_id` so other commands can reference it.

## §3. Get Catalog Details

```bash
meta ads catalog get "$CATALOG_ID" --output json | jq .
```

Present key fields: `name`, `id`, `vertical`, `product_count`, `feed_count`, `business`, `created_time`.

## §4. Connect Catalog to a Pixel

This is **the** unlock the CLI provides — wiring a catalog to a Meta Pixel for product-level conversion tracking. The CLI does both halves of the connection in one call:

```bash
meta ads dataset connect "$PIXEL_ID" \
  --ad-account-id "$AD_ACCOUNT_ID" \
  --catalog-id "$CATALOG_ID"

case $? in
  0) echo "Connected: pixel $PIXEL_ID ↔ catalog $CATALOG_ID ↔ ad account $AD_ACCOUNT_ID" ;;
  3) echo "ACCESS_TOKEN invalid"; exit 3 ;;
  4) echo "Connection failed (API error)"; exit 4 ;;
esac
```

Verify the connection:

```bash
meta ads dataset get "$PIXEL_ID" --output json | jq '{name, id, connected_catalogs, connected_ad_accounts}'
```

## §5. Delete Catalog

```bash
meta ads catalog delete "$CATALOG_ID"
# Or with --force to skip confirmation
meta ads catalog delete "$CATALOG_ID" --force
```

The CLI rejects deletion of catalogs with active product feeds or referencing ads. If you hit that, surface the error to the user and suggest first detaching the feeds/ads in Meta Commerce Manager.

## Populating Products (out of scope for this command)

The Ads CLI **does not yet** expose `product-item` commands as of April 30, 2026 (the blog post mentioned them, but the docs/command-reference do not). To populate a catalog with products today, choose one:

1. **Meta Commerce Manager UI** — manual or CSV upload at https://business.facebook.com/commerce
2. **Product feed URL** — host a CSV/XML feed at a stable URL and configure Meta to pull it on a schedule (Commerce Manager → Catalog → Data Sources → Add Data Source → Use a data feed)
3. **Graph API** (advanced) — POST to `/{catalog_id}/products` for individual product items. Requires `catalog_management` scope (already in the plugin's required scopes list).

When `meta ads product-item create` ships in a future CLI release, this command will grow a `/gtm-catalog sync` subcommand that pulls products from Stripe (or other detected commerce sources) and pushes them to the connected Meta catalog.

## Error Handling

- **`meta: command not found`** — Run `/gtm-setup`.
- **Exit code 3** — `ACCESS_TOKEN` missing/expired/lacks `catalog_management` scope. Refresh token in Business Manager with the full scope set listed in `skills/meta-ads/rules/ads-cli.md`.
- **Exit code 4 with "Cannot delete catalog with active feeds"** — Detach feeds via Commerce Manager first.
- **No `business_id` available** — CLI auto-resolves from the configured ad account; if that fails, pass `--business-id` explicitly or set `BUSINESS_ID` in `.env.gtm`.
