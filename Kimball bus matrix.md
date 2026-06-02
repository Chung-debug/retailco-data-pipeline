# Final Kimball Bus Matrix

## Conformed Dimensions

The dimensional model is designed around six conformed dimensions:

- `dim_date`
- `dim_customer` *(SCD2)*
- `dim_product` *(SCD2)*
- `dim_store`
- `dim_employee`
- `dim_payment_method`

---

## Bus Matrix

| Fact Table | Fact Type | Business Process | Grain | dim_date | dim_customer (SCD2) | dim_product (SCD2) | dim_store | dim_employee | dim_payment_method |
|---|---|---|---|---|---|---|---|---|---|
| `fct_sales` | Transactional | Sales transactions | One row per order line | Included | Included | Included | Included | Included | Not applicable |
| `fct_payments` | Transactional | Payment events | One row per payment event | Included | Included | Not applicable | Included | Not applicable | Included |
| `fct_inventory_daily` | Periodic Snapshot | Inventory position snapshots | One row per product per store per day | Included | Not applicable | Included | Included | Not applicable | Not applicable |
| `fct_order_lifecycle` | Accumulating Snapshot | Order fulfilment lifecycle | One row per order | Included | Included | Not applicable | Included | Included | Not applicable |

---

## Explanation

This Kimball bus matrix represents the target-state dimensional design for the Retailco warehouse. It is organized around four business processes:

- sales transactions
- payment events
- inventory position monitoring
- order fulfilment lifecycle

The design uses six conformed dimensions so that analytical reporting can remain consistent across facts.

The choice of fact types follows Kimball principles:

- **Transactional facts** capture atomic business events such as sales and payments
- **Periodic snapshot facts** capture inventory position over time at a fixed reporting grain
- **Accumulating snapshot facts** capture the progress of an order across lifecycle milestones

This design is intended to support management reporting, cross-process analysis, and future warehouse expansion without mirroring the source API directly.

---

## Submission Note

This bus matrix should be treated as the warehouse **design artifact**. It expresses the intended Kimball dimensional structure required by the brief and should be presented as the dimensional blueprint for the solution.
