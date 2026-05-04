# PPL Backend Documentation (Real-time Cricket Management)


## 1. Project Overview / প্রজেক্ট ওভারভিউ

PPL (Premier Player League) is a high-performance cricket tournament backend. It uses an invite-only player registration system and Django Channels (WebSockets) for real-time live scoring updates.

পিপিএল (প্রিমিয়ার প্লেয়ার লীগ) হলো একটি হাই-পারফরম্যান্স ক্রিকেট টুর্নামেন্ট ব্যাকএন্ড। এতে ডেটা সিকিউরিটির জন্য 'ইনভাইট-অনলি' প্লেয়ার রেজিস্ট্রেশন এবং লাইভ স্কোরিংয়ের জন্য জ্যাঙ্গো চ্যানেলস (WebSockets) ব্যবহার করা হয়েছে।

---

## 2. Updated Tech Stack / আপডেট করা টেক স্ট্যাক
* **Backend:** Django, Django REST Framework (DRF)
* **Real-time:** Django Channels (WebSockets)
* **Message Broker:** Redis (Required for Channel Layers)
* **Database:** PostgreSQL (Recommended)
* **Server:** Daphne (To handle both HTTP and WebSockets)

---

## 3. Core Models & Role Logic / কোর মডেল এবং রোল লজিক

### User & Roles (Access Control)
* **User Roles:** `Admin`, `Captain`, `Player`, `Viewer`.
* **Signup Flow:** - Default Role: `Viewer` (সরাসরি সাইন-আপ করলে সবাই ভিউয়ার)।
    - Captain: Assigned manually by Admin.
    - Player: Role updated from `Viewer` to `Player` only after accepting an invite.

### Invitation System
* **Invitation:** `team (FK)`, `token (Unique)`, `usage_limit (15)`, `is_active (Boolean)`.
* **Logic:** এই লিঙ্কের মাধ্যমে জয়েন করলেই কেবল ইউজার 'Player' লিস্টে আসবে এবং স্কোরিংয়ে তার নাম দেখাবে।

---

## 4. Real-time Architecture / রিয়েল-টাইম আর্কিটেকচার

### WebSocket Implementation
* **Consumer:** `ScoreConsumer` হ্যান্ডেল করবে দর্শকদের কানেকশন।
* **Channel Groups:** প্রতিটি ম্যাচের জন্য আলাদা গ্রুপ থাকবে (যেমন: `match_{id}`).
* **Trigger Mechanism:** - যখনই `Ball` মডেলে নতুন ডেটা সেভ হবে, ব্যাকএন্ড থেকে একটি সিগন্যাল (Django Signal) ওয়েব-সকেট গ্রুপে মেসেজ পাঠাবে। 
    - দর্শকরা পেজ রিফ্রেশ ছাড়াই লাইভ রান, উইকেট এবং ওভার আপডেট দেখতে পাবে।



---

## 5. Key Workflows / প্রধান কাজের ধাপসমূহ

### A. Team Setup & Player Onboarding
1. **Admin** ক্যাপ্টেন তৈরি করবেন।
2. **Captain** ইনভিটেশন লিঙ্ক শেয়ার করবেন।
3. **Player** লিঙ্কে ক্লিক করে টিমে যুক্ত হবেন (রোল অটো-আপডেট হবে)।
4. **Verification:** পেমেন্ট সম্পন্ন হলে টিম 'Verified' হবে এবং ম্যাচে অংশ নিতে পারবে।

### B. Live Scoring Flow
1. **Captain** বল-বাই-বল ডেটা এন্ট্রি দেবেন (API: `/api/score/ball/`).
2. **Backend:** রান এবং স্ট্যাটস আপডেট করবে এবং সাথে সাথে **WebSocket** ট্রিগার করবে।
3. **Viewer:** সাথে সাথে লাইভ স্কোরবোর্ড আপডেট দেখবে।

---

## 6. API & WebSocket Endpoints / এপিআই এবং সকেট এন্ডপয়েন্ট

### HTTP APIs
* `POST /api/auth/register/` - সাধারণ রেজিস্ট্রেশন (Role: Viewer).
* `POST /api/invite/generate/` - ক্যাপ্টেন লিঙ্ক তৈরি করবেন।
* `POST /api/invite/accept/{token}/` - প্লেয়ার হিসেবে জয়েন করা।
* `POST /api/score/ball/` - বল সেভ করা (Only Captain/Admin).

### WebSocket URL
* `ws://domain.com/ws/match/{match_id}/` - লাইভ স্কোর শোনার জন্য দর্শকদের কানেকশন।

---

## 7. Future Roadmap / ভবিষ্যৎ পরিকল্পনা
* **Payment Gateway:** SSLCommerz/bKash ইন্টিগ্রেশন।
* **Social Post System:** দর্শক এবং প্লেয়ারদের জন্য পোস্ট ও কমেন্ট ফিচার।
* **Advanced Analytics:** প্লেয়ারদের পারফরম্যান্স গ্রাফ এবং চার্ট।

---

## 8. Development Order / ডেভেলপমেন্ট সিকোয়েন্স
১. **Core Auth:** ইউজার রোল এবং ইনভিটেশন সিস্টেম।
২. **Scoring Engine:** বল-বাই-বল এন্ট্রি এবং অ্যাগ্রিগেশন।
৩. **Real-time:** Django Channels এবং Redis সেটআপ।
৪. **Payment:** ভেরিফিকেশন সিস্টেম।