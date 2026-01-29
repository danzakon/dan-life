# React Ecosystem vs Flutter: Technology Recommendation

**Prepared for:** PSG Platform
**Prepared by:** Tenex Labs
**Date:** January 2026

---

## Executive Summary

PSG is evaluating two approaches for building its platform:

| Approach | Web | Mobile | Language |
|----------|-----|--------|----------|
| **React Ecosystem** | React + Vite | React Native | TypeScript |
| **Flutter Everywhere** | Flutter Web | Flutter Mobile | Dart |

**Our recommendation: React Ecosystem.**

Flutter's "write once, run everywhere" promise is appealing, but Flutter Web has significant limitations for business dashboards. React is purpose-built for web and remains the industry standard, while React Native provides a natural path to mobile when needed.

This document outlines the technical and business rationale.

---

## The Core Question

Flutter promises one codebase for web, mobile, and desktop. Why not use it for everything?

**The answer:** Flutter Web is not equivalent to Flutter Mobile. While Flutter excels at mobile development, Flutter Web has documented limitations that make it a poor choice for business-critical web applications like PSG Platform.

---

## Part 1: Why React + Vite for Web (Not Flutter Web)

### 1.1 Flutter Web's Rendering Model Is Fundamentally Different

Flutter Web doesn't use standard HTML, CSS, or the DOM. Instead, it renders everything to a **canvas element** using WebGL (CanvasKit renderer).

| Aspect | React | Flutter Web |
|--------|-------|-------------|
| Rendering | Standard HTML/CSS/DOM | Canvas (WebGL) |
| Text selection | Native browser behavior | Custom implementation |
| Right-click menus | Native browser behavior | Must be custom-built |
| Find on page (Ctrl+F) | Works automatically | Doesn't work |
| Browser extensions | Work normally | Often don't work |
| Copy/paste | Native | Custom implementation |

**For a business dashboard where KAMs need to copy data, use browser features, and work efficiently, Flutter Web's canvas-based approach creates friction.**

### 1.2 Bundle Size and Initial Load Time

Flutter Web has a well-documented bundle size problem:

| Component | Size |
|-----------|------|
| CanvasKit renderer | ~1.5 MB |
| Flutter framework | Additional overhead |
| Application code | On top of above |
| **Typical Flutter Web app** | **2-5+ MB initial download** |

A typical React + Vite application with the same functionality loads in **200-500 KB**.

This matters because:
- KAMs may access the dashboard from various network conditions
- First impressions matter — slow loads feel unpolished
- Google's Core Web Vitals penalize slow initial loads

### 1.3 SEO and Discoverability

| Aspect | React | Flutter Web |
|--------|-------|-------------|
| Server-side rendering | Yes (Next.js) | Limited/complex |
| Search engine crawling | Standard HTML | Canvas content invisible |
| Social sharing previews | Works out of box | Requires workarounds |
| Deep linking | Native support | Requires configuration |

While PSG Platform is primarily a dashboard (not a marketing site), SEO matters for:
- Help documentation and support pages
- Any public-facing components
- Future expansion possibilities

### 1.4 Accessibility (WCAG Compliance)

Flutter Web's canvas-based rendering creates accessibility challenges:

| Aspect | React | Flutter Web |
|--------|-------|-------------|
| Screen reader support | Native HTML semantics | Requires parallel DOM overlay |
| Keyboard navigation | Standard browser behavior | Custom implementation |
| WCAG compliance | Straightforward | Requires significant effort |
| Audit risk | Low | Higher |

Enterprise clients increasingly require accessibility compliance. React's use of standard HTML elements makes this straightforward. Flutter Web requires building a parallel "semantics tree" that maps to DOM elements — adding complexity and potential for gaps.

### 1.5 Ecosystem and Libraries

| Ecosystem | React (npm) | Flutter/Dart (pub.dev) |
|-----------|-------------|------------------------|
| Total packages | 2M+ | ~50K |
| Data tables | AG Grid, TanStack Table, etc. | Limited options |
| Charts | Recharts, Victory, Nivo, etc. | fl_chart, syncfusion |
| Forms | React Hook Form, Formik | Limited options |
| Date pickers | Dozens of mature options | Fewer, less mature |
| Enterprise UI kits | MUI, Ant Design, Chakra | Limited |

**For a data-heavy dashboard with tables, charts, and complex forms, React's ecosystem is vastly more mature.**

### 1.6 Developer Talent

| Metric | React/TypeScript | Dart/Flutter |
|--------|------------------|--------------|
| Stack Overflow 2025 most used | Top 5 | Not in top 10 |
| Job postings | Ubiquitous | Niche |
| Bootcamp graduates | Millions | Few |
| Freelance availability | High | Limited |

Hiring React developers is straightforward. Hiring Dart developers who can also build production web applications is significantly harder.

### 1.7 Summary: Web Framework Comparison

| Factor | React + Vite | Flutter Web |
|--------|--------------|-------------|
| Native web behavior | Yes | No (canvas) |
| Bundle size | Small (200-500KB) | Large (2-5MB+) |
| Initial load speed | Fast | Slow |
| SEO capability | Excellent | Poor |
| Accessibility | Native HTML | Complex workarounds |
| Ecosystem maturity | 10+ years | ~5 years for web |
| Library availability | Vast | Limited |
| Talent pool | Massive | Small |
| Production web apps | Billions | Few |

**React is the industry standard for web applications for good reasons. Flutter Web is experimental by comparison.**

---

## Part 2: Why React Native for Mobile (When the Time Comes)

PSG's mobile app is Phase 3 — a "companion" app, not the primary product. When that time comes:

### 2.1 Code Sharing with Existing Codebase

| What Can Be Shared | React Native | Flutter |
|--------------------|--------------|---------|
| TypeScript types | Yes | No (rewrite in Dart) |
| Zod validation schemas | Yes | No (rewrite in Dart) |
| API client code | Yes | No (rewrite in Dart) |
| Business logic | Yes | No (rewrite in Dart) |
| Utility functions | Yes | No (rewrite in Dart) |

With React Native, the mobile app inherits everything already built for web and backend. With Flutter, it starts from zero.

### 2.2 Team Efficiency

| Scenario | React Native | Flutter |
|----------|--------------|---------|
| Web dev helps with mobile | Immediately productive | Must learn Dart |
| Bug in shared logic | Fix once | Fix in two places |
| New API endpoint | Update shared client | Update two clients |
| Type changes | Propagate automatically | Manual sync required |

### 2.3 The Companion App Use Case

The Phase 3 mobile app will likely include:
- Dashboard summaries
- Push notification responses
- Quick data lookups
- Approval workflows

This is **exactly what React Native excels at** — standard business UI with forms, lists, and data display. Flutter's advantages (complex animations, custom rendering, games) are irrelevant.

---

## Part 3: The "One Codebase" Myth

Flutter's pitch is "one codebase for everything." In practice:

### 3.1 Web and Mobile Are Different Products

| Consideration | Web Dashboard | Mobile Companion |
|---------------|---------------|------------------|
| Screen size | Large monitors | Phone screens |
| Input method | Mouse + keyboard | Touch |
| Usage patterns | Long sessions, complex tasks | Quick checks |
| Navigation | Sidebar, tabs, breadcrumbs | Bottom nav, stacks |
| Data density | High (tables, dashboards) | Low (summaries) |

A web dashboard and a mobile companion app require different UX anyway. Sharing 100% of UI code isn't realistic or desirable.

### 3.2 What Actually Gets Shared

With React Ecosystem:

| Layer | Shared? |
|-------|---------|
| Types and interfaces | Yes |
| API clients | Yes |
| Validation logic | Yes |
| Business logic | Yes |
| UI components | Some (with React Native Web) |

With Flutter:

| Layer | Shared? |
|-------|---------|
| Everything | Yes, but... |
| Web-specific optimizations | Compromised |
| Mobile-specific optimizations | Compromised |
| Platform conventions | Often ignored |

**Sharing UI code between web and mobile often means compromising both.** Sharing business logic while building platform-appropriate UIs is the better approach.

---

## Part 4: Risk Assessment

### 4.1 Flutter Web Risks

| Risk | Concern |
|------|---------|
| Maturity | Flutter Web is newer and less battle-tested than React |
| Bundle size | May cause performance issues for users |
| Accessibility | May require significant extra work or create compliance gaps |
| Talent | Harder to hire and ramp up developers |
| Lock-in | Dart skills don't transfer to other projects |
| Google's track record | Google has discontinued many products (Stadia, Google+, etc.) |

### 4.2 React Ecosystem Risks

| Risk | Mitigation |
|------|------------|
| Two frameworks (React + React Native) | Same language, shared code, proven at scale |
| Meta could change direction | React is open source with massive community; Microsoft, Shopify, Amazon all contribute |

---

## Part 5: Who Uses What

### React for Web (Sampling)

Nearly every major web application uses React or a React-based framework:
- Facebook, Instagram (Meta)
- Netflix, Airbnb, Uber
- Shopify Admin
- Discord Web
- Notion, Figma
- Virtually all modern SaaS dashboards

### Flutter Web in Production

Flutter Web production deployments are rare and typically limited to:
- Internal tools where SEO/accessibility matter less
- Marketing microsites
- Apps where mobile-first Flutter was extended to web as secondary

**There's a reason the industry standard for web applications is React, not Flutter.**

---

## Part 6: PSG-Specific Recommendation

### What PSG Is Building

| Component | Requirements |
|-----------|--------------|
| KAM Dashboard | Data tables, charts, complex forms, real-time updates |
| Line Review Generator | Document preview, editing, export |
| AI Chat Interface | Streaming responses, rich cards |
| Account Management | CRUD operations, relationships |
| Data Upload | File handling, validation, preview |

**Every one of these is better served by React's mature ecosystem than Flutter Web's canvas-based approach.**

### The Right Architecture for PSG

| Layer | Technology | Rationale |
|-------|------------|-----------|
| Web Dashboard | React + Vite + TypeScript | Industry standard, mature ecosystem, fast |
| Backend API | Fastify + TypeScript | Shares types with frontend |
| Mobile (Phase 3) | React Native | Shares code with web, same language |
| Shared Code | TypeScript packages | Types, validation, API clients |

### PSG Platform Fit Assessment

| Factor | React Ecosystem | Flutter Everywhere |
|--------|-----------------|-------------------|
| Web dashboard performance | Excellent | Compromised |
| Data table/chart libraries | Vast selection | Limited |
| Initial load speed | Fast | Slow |
| Accessibility compliance | Straightforward | Complex |
| SEO capability | Native | Poor |
| Talent availability | Abundant | Scarce |
| Code sharing (web ↔ mobile) | Types, logic, validation | UI code (with tradeoffs) |
| Code sharing (web ↔ backend) | Full | None |
| Long-term maintainability | Proven | Unknown |
| **Overall Fit** | **Strong** | **Poor** |

---

## Conclusion

Flutter is an excellent mobile framework. Flutter Web is not ready for business-critical web applications.

PSG Platform is primarily a **web dashboard** with a future **mobile companion**. The React ecosystem provides:

1. **A mature, battle-tested web framework** with the libraries and tooling needed for data-heavy dashboards
2. **Native web behavior** that users expect (text selection, browser features, accessibility)
3. **Fast performance** with small bundle sizes
4. **A clear path to mobile** that shares code without compromising the web experience
5. **Abundant talent** for hiring and scaling

For PSG's specific needs, **React + Vite for web and React Native for mobile is the right choice.**

---

## Sources

### Flutter Web Limitations

- [Flutter Blog: Accessibility in Flutter on the Web](https://blog.flutter.dev/accessibility-in-flutter-on-the-web-51bfc558b7d3) — Official documentation on canvas accessibility challenges
- [Flutter Blog: Best practices for optimizing Flutter web loading speed](https://blog.flutter.dev/best-practices-for-optimizing-flutter-web-loading-speed-7cc0df14ce5c) — Official acknowledgment of load time issues
- [Is Flutter Web Ready for Prime Time in 2025?](https://medium.com/@aman.flutternest/is-flutter-web-ready-for-prime-time-in-2025-541493ec2d69) — Community analysis
- [When to Use Flutter for Web in 2025](https://www.milanmeurrens.com/guides/when-to-use-flutter-for-web-in-2025-a-comprehensive-guide) — CanvasKit rendering explanation

### React Native at Scale

- [Five Years of React Native at Shopify](https://shopify.engineering/five-years-of-react-native-at-shopify) — Shopify Engineering, January 2025
- [How Discord Achieves Native iOS Performance with React Native](https://discord.com/blog/how-discord-achieves-native-ios-performance-with-react-native) — Discord Engineering
- [React Native Showcase](https://reactnative.dev/showcase) — Companies using React Native

### Industry Data

- [Stack Overflow Developer Survey 2025](https://survey.stackoverflow.co/2025/technology) — Framework popularity and usage
- [State of React 2024](https://www.telerik.com/blogs/top-libraries-tools-modern-react-frontend-development) — React ecosystem analysis
