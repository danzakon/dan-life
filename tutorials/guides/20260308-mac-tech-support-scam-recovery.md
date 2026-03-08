# Mac Recovery: After a Tech Support Scam

What to do if someone gained remote access to your Mac, asked for your password, or tricked you into giving them control of your computer.

---

## Overview

Tech support scammers impersonate companies like Apple, HP, or Microsoft. They gain remote access to your machine, collect passwords and personal data, and often install backdoors for future access. This guide walks through how to lock them out and secure your accounts.

```
Threat model after a scam call:
┌─────────────────────────────────────────────────────┐
│  What they may have seen:                           │
│  - Your screen (everything visible while connected) │
│  - Saved passwords in your browser                  │
│  - Your Mac login password (if you typed it)        │
│  - Open email / banking tabs                        │
│  - Personal info (name, address, etc.)              │
│                                                     │
│  What they may have installed:                      │
│  - Remote access software                           │
│  - Configuration profiles                           │
│  - Browser extensions / malware                     │
└─────────────────────────────────────────────────────┘
```

---

## Step 1: Disconnect from the Internet

Do this immediately to cut off any active remote session.

- Click the **Wi-Fi icon** in the menu bar (top right of screen)
- Click **Turn Wi-Fi Off**
- If using an ethernet cable, unplug it

You can reconnect once you've worked through Steps 2–4.

---

## Step 2: Remove Remote Access Software

Scammers commonly install tools like AnyDesk, TeamViewer, or ScreenConnect. Check for them first.

### Check Applications

- Open **Finder** > **Applications**
- Click the list view icon and sort by **Date Added**
- Look for anything installed recently that you don't recognize

Common scam tools to look for:

| App Name | Notes |
|---|---|
| AnyDesk | Orange logo |
| TeamViewer | Blue icon with arrows |
| ScreenConnect / ConnectWise | May appear as "Support" or "Client" |
| GoToAssist | Citrix/GoTo branding |
| Splashtop | Blue "S" icon |
| LogMeIn Rescue | May have a generic name |

To uninstall: drag the app to the **Trash**, then empty the Trash.

### Check for Leftover Files

Open **Finder** > **Go** menu > **Go to Folder** and check each of these:

- `~/Library/Application Support/`
- `~/Library/LaunchAgents/`
- `/Library/LaunchDaemons/`

Delete any folders matching the names above.

### Turn Off Built-in Screen Sharing

Go to **Apple menu () > System Settings > General > Sharing**

Make sure all of these are **OFF**:

- [ ] Screen Sharing
- [ ] Remote Management
- [ ] Remote Login
- [ ] Remote Apple Events

### Check for Configuration Profiles

Go to **Apple menu () > System Settings > General > Device Management**

- If this section doesn't appear, no profiles are installed (good)
- If it appears and shows profiles you didn't install, select each and click the minus (−) button to remove

### Check Login Items

Go to **Apple menu () > System Settings > General > Login Items & Extensions**

Review everything under **Open at Login** and **Allow in the Background**. Remove anything unfamiliar by selecting it and clicking the minus (−) button.

---

## Step 3: Change All Passwords

**Do this from a different device** (phone or another computer) — not the compromised Mac.

### Priority Order

- [ ] **Apple ID** — [appleid.apple.com](https://appleid.apple.com)
- [ ] **Mac login password** — change this on the Mac itself after the other steps
- [ ] **Email** (Gmail, Yahoo, iCloud, etc.)
- [ ] **Banking and financial sites**
- [ ] **Any account where a password was saved in Safari or Chrome**

Assume they could see anything on screen while they had access, including saved passwords, open tabs, and email.

### Change Mac Login Password (on the Mac)

**Apple menu () > System Settings > Users & Groups > Change Password**

---

## Step 4: Enable Two-Factor Authentication

Even if they captured a password, 2FA blocks them from using it.

**Start with these accounts:**

- **Apple ID**: System Settings > [your name at top] > Sign-In & Security > Two-Factor Authentication
- **Email**: Look for "Security" in your email provider's account settings
- **Banking**: Call the bank directly — they'll walk you through it

Use an authenticator app (Google Authenticator or the built-in Apple Passwords app) rather than SMS when given the option. SMS 2FA is still much better than nothing.

---

## Step 5: Scan for Malware

- Download **Malwarebytes for Mac** (free version): [malwarebytes.com](https://www.malwarebytes.com)
- Run a full scan
- Remove anything it flags

---

## Step 6: Check Browser Extensions

**Safari:** Safari menu > Settings > Extensions — remove anything you didn't install

**Chrome:** Type `chrome://extensions/` in the address bar — remove anything unfamiliar

Then clear browser data in whichever browser you use (cookies, saved forms, cached data).

---

## Step 7: Contact Your Bank

Even if you didn't give them payment info directly:

- [ ] Call your bank and credit card companies
- [ ] Tell them the computer was compromised and to flag the account for suspicious activity
- [ ] If you paid the scammers, **dispute the charge immediately**
- [ ] Ask to enable transaction alerts (text or email for every charge)

---

## Step 8: Set Up Fraud Alerts or Credit Freeze

If you shared personal info (name, address, date of birth, Social Security number), contact the credit bureaus. Calling one is enough — they're required to notify the other two.

| Bureau | Phone |
|---|---|
| Equifax | 1-800-525-6285 |
| Experian | 1-888-397-3742 |
| TransUnion | 1-800-680-7289 |

- **Fraud alert**: Free, lasts 1 year, flags your credit file so lenders must verify identity before issuing credit
- **Credit freeze**: Free, stronger — completely blocks new accounts from being opened in your name

---

## Step 9: Report the Scam

- **FTC**: [ReportFraud.ftc.gov](https://reportfraud.ftc.gov) — takes 5 minutes, creates a paper trail
- **FBI IC3**: [ic3.gov](https://ic3.gov) — especially if money was lost
- **Apple**: [support.apple.com/en-us/102568](https://support.apple.com/en-us/102568) — report phishing and tech support scams

---

## Step 10 (Nuclear Option): Erase and Reinstall macOS

If you're not confident you found everything, a clean reinstall is the safest path. This wipes everything and guarantees no backdoors remain.

**Before erasing:**
- Back up personal files (Documents, Photos, Desktop) to a USB drive or iCloud

**To enter Recovery Mode:**

| Mac Type | How to Enter Recovery |
|---|---|
| Apple Silicon (M1, M2, M3, M4) | Hold the **power button** until "Loading startup options" appears |
| Intel Mac | Hold **Command (⌘) + R** immediately after pressing power |

**In Recovery Mode:**
1. Open **Disk Utility** > select the main drive > **Erase**
2. Quit Disk Utility
3. Select **Reinstall macOS**
4. Follow the prompts
5. Restore personal files from backup after setup

---

## Watch Out for Follow-Up Scams

Scam victims are frequently targeted again. Common follow-up calls:

- "We're from Apple Security — we detected unauthorized access on your account"
- "We're from your bank's fraud department — we need to verify your identity"
- "We're from the FTC — we recovered your money, we just need your bank details"

**The rule: if someone calls YOU about a problem, hang up.** If you're worried it's real, look up the official phone number yourself and call back independently.

---

## Checklist Summary

```
IMMEDIATE
[ ] Disconnect from Wi-Fi

REMOTE ACCESS
[ ] Check Applications for remote tools and uninstall any
[ ] Turn off Screen Sharing, Remote Management, Remote Login
[ ] Check for configuration profiles — remove any unknown ones
[ ] Check Login Items — remove anything unfamiliar

PASSWORDS (from a different device)
[ ] Change Apple ID password
[ ] Change email password
[ ] Change banking / financial passwords
[ ] Change other saved passwords
[ ] Change Mac login password (on the Mac)

SECURITY
[ ] Enable 2FA on Apple ID
[ ] Enable 2FA on email
[ ] Enable 2FA on banking
[ ] Run Malwarebytes scan
[ ] Check and clean browser extensions

FINANCIAL
[ ] Call bank and credit card companies
[ ] Dispute any charges from the scammers
[ ] Enable transaction alerts
[ ] Set up fraud alert or credit freeze (if personal info was shared)

REPORTING
[ ] Report to FTC at ReportFraud.ftc.gov
[ ] Report to FBI IC3 at ic3.gov (if money was lost)
```
