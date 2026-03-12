# FoodDash Payment Flow Usability Study

## Study Overview

**Type:** Moderated usability study
**Participants:** n=20
**Date:** January 18-22, 2025
**Facilitator:** UX Research Team (Rachel Kim, Lead Researcher)
**Objective:** Evaluate the end-to-end ordering and payment experience across platforms

Participants were recruited from active FoodDash users across iOS (n=10), Android (n=6), and Web (n=4) platforms. Each session lasted approximately 30 minutes and involved completing a series of ordering tasks.

---

## December Baseline (Previous Study)

A baseline usability study was conducted **December 5-8, 2024** with n=15 participants.

| Metric | December Baseline |
|--------|------------------|
| Payment flow satisfaction score | 4.2 / 5.0 |
| Task completion rate (place an order) | 92% |
| Average payment processing time | 3.2 seconds |
| Users reporting payment issues | 1/15 (6.7%) |
| Average time from checkout to confirmation | 8.4 seconds |

**Notable findings from December:**
- Payment flow was rated as "intuitive" by 13/15 participants
- One participant experienced a payment failure due to expired card (expected behavior)
- Restaurant search was the primary area of friction (addressed in Dec 18 update)
- Overall app satisfaction: 4.4/5.0

---

## January Findings

### Task Completion

| Metric | December Baseline | January Study | Change |
|--------|------------------|---------------|--------|
| Task completion rate | 92% | 54% | -38pp |
| Average payment processing time | 3.2s | 12.8s | +300% |
| Payment flow satisfaction | 4.2/5 | 1.8/5 | -57% |
| Users experiencing payment delays >5s | 1/15 | 8/20 | Significant increase |
| Users who abandoned checkout | 1/15 | 9/20 | Significant increase |

### Platform Comparison

| Platform | Task Completion Rate | Avg Processing Time | Payment Errors Observed |
|----------|---------------------|--------------------|-----------------------|
| iOS (n=10) | 41% | 18.3s | 7/10 participants |
| Android (n=6) | 89% | 4.1s | 1/6 participants |
| Web (n=4) | 86% | 3.8s | 0/4 participants |

**Note:** The disparity between iOS and other platforms was stark and consistent across all iOS test devices (iPhone 14, iPhone 15, iPhone SE).

---

## Key Themes

### 1. Payment Timeouts (Reported by 8/10 iOS users)
Participants on iOS consistently experienced long payment processing times. The spinner would appear after tapping "Pay Now" and persist for 10-45 seconds before either succeeding or displaying an error.

> "I tapped pay and then just... waited. It felt like the app was frozen." — Participant 7 (iOS)

### 2. Confusing Error Messages
When payments failed, the error message displayed was: **"Something went wrong. Please try again."**

- No specific information about *what* went wrong
- No indication of whether the payment was actually charged
- 6/8 affected users expressed frustration with the vague messaging

> "Something went wrong? That's all you're going to tell me? Did it charge my card or not?" — Participant 3 (iOS)

### 3. No Retry Mechanism
After a payment failure, users were returned to the cart screen with no option to retry the payment. They had to go through the entire checkout flow again.

- Average time to re-attempt: 45 seconds
- 3 participants gave up after 2 failed attempts
- 2 participants gave up after 3 failed attempts

> "Why do I have to re-enter everything? Just let me try again." — Participant 11 (iOS)

### 4. Inconsistent Behavior
Some participants noted that the same payment method would fail multiple times and then inexplicably succeed, suggesting an intermittent issue rather than a permanent one.

### 5. Cart Abandonment
9 out of 20 participants abandoned their cart during the study. All 9 were iOS users.

---

## Workarounds Observed

During the study, participants independently discovered or attempted several workarounds:

1. **Switched to Android device** — 3 iOS participants asked if they could try on a different device. When allowed, all 3 successfully completed payment on an Android phone.
2. **Used PayPal instead of Apple Pay** — 2 participants switched payment methods. One succeeded with PayPal (after 2 Apple Pay failures), one still failed.
3. **Asked friend to order** — 1 participant said they would ask their friend (who has an Android phone) to place the order for them.

---

## Risk Assessment

### Churn Indicators
- **4 out of 20 participants** mentioned they were considering switching to a competitor app (UberEats, DoorDash, Grubhub)
- **2 participants** stated they had already started using a competitor due to ongoing payment issues
- **3 participants** said they would "give it one more week" before switching

### Sentiment Analysis
- iOS user satisfaction: 1.4/5.0 (down from 4.3/5.0 in December)
- Android user satisfaction: 4.1/5.0 (stable)
- Web user satisfaction: 4.0/5.0 (stable)

---

## Recommendations

1. **Improve error messaging** — Replace "Something went wrong" with specific, actionable error messages. Indicate clearly whether the payment was charged.

2. **Add retry mechanism** — Allow users to retry payment from the checkout screen without re-entering the full flow. Preserve cart state.

3. **Investigate iOS-specific payment issue** — The data strongly suggests a platform-specific regression. The payment processing path on iOS should be investigated urgently. The issue appears to affect all payment methods on iOS, but Apple Pay is disproportionately impacted.

4. **Add payment status indicator** — Show real-time processing status during payment (e.g., "Connecting to payment provider...", "Processing payment...", "Confirming with bank...").

5. **Implement timeout handling** — If payment processing exceeds 10 seconds, show a status update. If it exceeds 30 seconds, offer to cancel and retry.

---

## Appendix: Study Participants

| ID | Platform | Device | Payment Method | Task Completed |
|----|----------|--------|---------------|----------------|
| P1 | iOS | iPhone 15 | Apple Pay | No |
| P2 | iOS | iPhone 14 | Credit Card | No |
| P3 | iOS | iPhone 15 Pro | Apple Pay | No |
| P4 | Android | Pixel 7 | Google Pay | Yes |
| P5 | iOS | iPhone SE | Credit Card | Yes (3rd attempt) |
| P6 | Web | Chrome | Credit Card | Yes |
| P7 | iOS | iPhone 14 | Apple Pay | No |
| P8 | Android | Samsung S23 | Credit Card | Yes |
| P9 | iOS | iPhone 15 | Apple Pay | No |
| P10 | Web | Safari | PayPal | Yes |
| P11 | iOS | iPhone 14 Pro | Credit Card | No |
| P12 | Android | Pixel 7 | Google Pay | Yes |
| P13 | iOS | iPhone 15 | Apple Pay | Yes (4th attempt) |
| P14 | Android | Samsung S23 | Credit Card | Yes |
| P15 | Web | Chrome | Credit Card | Yes |
| P16 | iOS | iPhone SE | Apple Pay | No |
| P17 | Android | Samsung A54 | Google Pay | Yes |
| P18 | iOS | iPhone 14 | Credit Card | Yes (2nd attempt) |
| P19 | Web | Firefox | PayPal | Yes |
| P20 | Android | Pixel 7 Pro | Google Pay | No |
