# Requirements JSON

The generator reads one object. Prose is not an input. Map the user's story into this shape, then run the script. Do not add an acceptance line the user did not write or clearly confirm.

```json
{
  "feature": "Checkout",
  "stories": [
    {
      "id": "US-14",
      "title": "Apply a promo code",
      "persona": "shopper",
      "want": "apply one promo code at checkout",
      "outcome": "the order total shows the discount",
      "acceptance": [
        {"id": "AC-1", "text": "A valid unexpired code reduces the order total by the code amount"}
      ],
      "risks": {"impact": 5, "likelihood": 4, "areas": ["payment", "pricing"]},
      "fields": [
        {"name": "promo_code", "type": "string", "min_length": 4, "max_length": 12, "required": true}
      ],
      "states": [
        {
          "name": "promo",
          "transitions": [
            {"from": "empty", "event": "apply_valid", "to": "applied"}
          ]
        }
      ],
      "rules": [
        {"when": {"country": "US", "cart_total": "74.99"}, "then": "standard shipping"}
      ]
    }
  ]
}
```

`fields`, `states`, and `rules` may be omitted. `areas` uses the words in the risk model. Number fields need both `minimum` and `maximum`.

A full checkout example with promo codes, a shipping decision table, and a low-risk content story is in the project `examples/qa-test-generation/checkout.json`.
