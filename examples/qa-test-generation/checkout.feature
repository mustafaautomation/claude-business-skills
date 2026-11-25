Feature: Checkout
  Risk-based scenarios generated from the requirements file.
  Exploratory charters are written separately and are not in this file.

  @p0 @US-14 @acceptance @positive
  Scenario: US-14-TC-001 A valid unexpired code reduces the order total by the code amount
    Given A shopper can apply one promo code at checkout
    When The acceptance criterion holds: A valid unexpired code reduces the order total by the code amount
    Then the order total shows the discount

  @p0 @US-14 @acceptance @negative
  Scenario: US-14-TC-002 An expired code is rejected and the total stays unchanged
    Given A shopper can apply one promo code at checkout
    When The acceptance criterion holds: An expired code is rejected and the total stays unchanged
    Then The system refuses the action and leaves protected totals unchanged.

  @p0 @US-14 @acceptance @negative
  Scenario: US-14-TC-003 A second code is rejected while one code is already applied
    Given A shopper can apply one promo code at checkout
    When The acceptance criterion holds: A second code is rejected while one code is already applied
    Then The system refuses the action and leaves protected totals unchanged.

  @p0 @US-14 @boundary @positive
  Scenario: US-14-TC-004 promo_code length 4 is accepted
    Given A shopper can apply one promo code at checkout
    When promo_code is aaaa (length 4)
    Then The value is accepted.

  @p0 @US-14 @boundary @negative
  Scenario: US-14-TC-005 promo_code length 3 is rejected
    Given A shopper can apply one promo code at checkout
    When promo_code is aaa (length 3)
    Then The value is rejected with a validation message.

  @p0 @US-14 @boundary @positive
  Scenario: US-14-TC-006 promo_code length 12 is accepted
    Given A shopper can apply one promo code at checkout
    When promo_code is aaaaaaaaaaaa (length 12)
    Then The value is accepted.

  @p0 @US-14 @boundary @negative
  Scenario: US-14-TC-007 promo_code length 13 is rejected
    Given A shopper can apply one promo code at checkout
    When promo_code is aaaaaaaaaaaaa (length 13)
    Then The value is rejected with a validation message.

  @p0 @US-14 @boundary @negative
  Scenario: US-14-TC-008 promo_code is empty and is rejected
    Given A shopper can apply one promo code at checkout
    When promo_code is empty
    Then The value is rejected with a validation message.

  @p0 @US-14 @state-transition @positive
  Scenario: US-14-TC-009 promo: empty --apply_valid--> applied
    Given A shopper can apply one promo code at checkout
    When The promo state is empty and apply_valid happens
    Then The state is applied.

  @p0 @US-14 @state-transition @negative
  Scenario: US-14-TC-010 promo: applied --apply_second--> applied
    Given A shopper can apply one promo code at checkout
    When The promo state is applied and apply_second happens
    Then The event is rejected and the state stays applied.

  @p0 @US-14 @state-transition @positive
  Scenario: US-14-TC-011 promo: applied --remove--> empty
    Given A shopper can apply one promo code at checkout
    When The promo state is applied and remove happens
    Then The state is empty.

  @p0 @US-30 @acceptance @positive
  Scenario: US-30-TC-001 Carts at or above 75.00 in the US show free shipping
    Given A shopper can see the shipping price the cart actually qualifies for
    When The acceptance criterion holds: Carts at or above 75.00 in the US show free shipping
    Then the shipping line shows the price from the rule

  @p0 @US-30 @boundary @positive
  Scenario: US-30-TC-002 cart_total at minimum 0 is accepted
    Given A shopper can see the shipping price the cart actually qualifies for
    When cart_total is 0
    Then The value is accepted.

  @p0 @US-30 @boundary @negative
  Scenario: US-30-TC-003 cart_total below minimum (-0.01) is rejected
    Given A shopper can see the shipping price the cart actually qualifies for
    When cart_total is -0.01
    Then The value is rejected with a validation message.

  @p0 @US-30 @boundary @positive
  Scenario: US-30-TC-004 cart_total at maximum 10000 is accepted
    Given A shopper can see the shipping price the cart actually qualifies for
    When cart_total is 10000
    Then The value is accepted.

  @p0 @US-30 @boundary @negative
  Scenario: US-30-TC-005 cart_total above maximum (10000.01) is rejected
    Given A shopper can see the shipping price the cart actually qualifies for
    When cart_total is 10000.01
    Then The value is rejected with a validation message.

  @p0 @US-30 @decision-table @positive
  Scenario: US-30-TC-006 rule country=US cart_total=74.99 -> standard shipping
    Given A shopper can see the shipping price the cart actually qualifies for
    When Conditions are country=US cart_total=74.99
    Then standard shipping

  @p0 @US-30 @decision-table @positive
  Scenario: US-30-TC-007 rule country=US cart_total=75.00 -> free shipping
    Given A shopper can see the shipping price the cart actually qualifies for
    When Conditions are country=US cart_total=75.00
    Then free shipping

  @p0 @US-30 @decision-table @positive
  Scenario: US-30-TC-008 rule country=CA cart_total=75.00 -> standard shipping
    Given A shopper can see the shipping price the cart actually qualifies for
    When Conditions are country=CA cart_total=75.00
    Then standard shipping

  @p3 @US-3 @acceptance @positive
  Scenario: US-3-TC-001 A dated estimate is visible before the pay button
    Given A shopper can read an estimated delivery date before paying
    When The acceptance criterion holds: A dated estimate is visible before the pay button
    Then the checkout page shows the estimated delivery date
