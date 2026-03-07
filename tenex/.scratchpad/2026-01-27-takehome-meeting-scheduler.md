# Take-Home Option A: Meeting Scheduler Agent

## Overview

Build a meeting scheduling assistant that coordinates meetings across multiple participants using real Google Calendar integration.

---

## The Product

You're building **CalBot**, an AI-powered meeting scheduler. Users interact with it through a chat interface to schedule meetings, and CalBot handles the complexity of checking real calendars, finding available times, and booking across multiple participants.

### Core User Flow

**User:** "Schedule a 30-min sync with alice@gmail.com and bob@gmail.com sometime next week"

**CalBot:** "I'll need to check everyone's calendars. Alice and Bob will need to connect their Google Calendar."

*Alice receives invite link, connects her calendar. Bob receives invite link, connects his calendar.*

**CalBot:** "Everyone's connected! Looking at calendars..."

"I found 3 times that work for everyone:
1. Tuesday 2:00 PM - 2:30 PM
2. Wednesday 10:00 AM - 10:30 AM
3. Thursday 4:00 PM - 4:30 PM

Which works best?"

**User:** "Let's do Tuesday"

**CalBot:** *creates event on everyone's calendars*

"Done! I've scheduled 'Sync' for Tuesday 2:00 PM. Calendar invites sent to all participants."

---

## What You're Building

### Frontend

A web application with:

1. **Chat Interface**
   - Conversational UI for interacting with CalBot
   - Message history persists within a session
   - Clear indication of when CalBot is "thinking"
   - Rich responses (clickable time options, participant status, etc.)

2. **Calendar View**
   - Visual display of the authenticated user's calendar
   - Shows existing events and newly scheduled meetings
   - Week view at minimum
   - Visual indication of other participants' availability (optional but nice)

3. **Participant Management**
   - See who's been invited to connect
   - Status of each participant (pending, connected, declined)
   - Ability to resend connection requests

4. **User Authentication**
   - Google OAuth sign-in for the primary user
   - Clear indication of connection status

### Backend

1. **Agent Logic**
   - Parses natural language scheduling requests
   - Determines what actions to take
   - Manages multi-turn conversations
   - Handles the state machine of "waiting for participants"

2. **Google Calendar Integration**
   - OAuth flow for multiple users
   - Read calendar events / free-busy information
   - Find overlapping availability across all participants
   - Create calendar events on all connected calendars

3. **Participant Invitation System**
   - Generate unique invite links for participants
   - Track who has connected and who hasn't
   - Handle the async nature of people connecting at different times

4. **State Management**
   - Track pending scheduling requests
   - Handle partial participant connections
   - Manage conversation context

---

## System Constraints

These constraints exist to make the problem realistic. You decide how to handle them.

### Multi-Party Scheduling

This is the core challenge. Real scheduling requires:

| Requirement | Details |
|-------------|---------|
| Multiple OAuth tokens | Each participant authenticates separately |
| Async participant joining | Alice might connect immediately, Bob might take hours |
| Partial availability checks | Can show "Alice is free, waiting on Bob" |
| All-party availability | Find times that work for everyone who's connected |
| Cross-timezone support | Participants may be in different timezones |

### Participant Connection Flow

```
User requests meeting with alice@gmail.com
         │
         ▼
System sends Alice an invite link (email, or display link to share)
         │
         ▼
Alice clicks link, authenticates with Google
         │
         ▼
System can now read Alice's calendar
         │
         ▼
Once all participants connected, find mutual availability
```

**Key decisions you'll make:**
- How do you notify participants? (email, shareable link, both)
- What if someone never connects?
- Can scheduling proceed with partial connections?
- How long are invite links valid?

### Scheduling Logic

- Meetings can have 2-6 participants (including the organizer)
- Default meeting duration is 30 minutes if not specified
- Meetings should only be scheduled during "working hours" (you define this)
- Handle timezone differences between participants
- Buffer time between meetings is a real consideration

### Conversation Complexity

The agent should handle:

| Scenario | Example |
|----------|---------|
| Simple request | "Schedule a call with alice@gmail.com tomorrow" |
| Underspecified | "Set up a meeting with the team" (who?) |
| No availability | What if there's no overlapping free time? |
| Partial connections | "Alice connected, still waiting on Bob" |
| Modifications | "Actually, make it an hour instead" |
| Rescheduling | "Move our Tuesday meeting to Wednesday" |
| Cancellations | "Cancel the meeting I just scheduled" |

### State & Persistence

- Conversation history persists within a session
- Pending invitations should survive page refresh
- Created meetings should appear on the calendar view
- Participant connection status should be tracked

---

## Google Calendar Integration Details

### Required

| Feature | Details |
|---------|---------|
| OAuth for organizer | Primary user signs in with Google |
| OAuth for participants | Each participant can connect their calendar |
| Read free/busy | Check when people are available |
| Read events | See existing calendar events |
| Create events | Book meetings on all connected calendars |

### Setup

You'll need:
- Google Cloud project with Calendar API enabled
- OAuth consent screen (can be in "testing" mode)
- OAuth credentials (web application type)

**Add our test emails as test users so we can evaluate:**
- [Include your evaluator emails here]

### Not Required

- Gmail API (calendar events auto-send invites)
- Outlook/other calendar providers
- Production OAuth verification
- Refresh token persistence beyond the session (nice to have)

---

## What We're NOT Specifying

These are intentional decisions for you to make:

- Tech stack (use whatever you're productive in)
- How you notify participants (email via SendGrid/Resend, shareable links, etc.)
- How the agent decides what to do (prompting strategy, tool use, etc.)
- How you handle the "waiting for participants" state
- How you structure the backend
- Visual design (functional > pretty, but UX should be coherent)
- How long invite links remain valid
- Whether partial scheduling (some participants connected) is allowed

---

## Deliverables

### 1. Hosted Application

Deploy your application somewhere accessible:
- Should be functional for us to test with real Google accounts
- Include setup instructions for OAuth testing

### 2. Source Code

- GitHub repo (can be private, invite us)
- Include a README with:
  - How to run locally
  - How to set up Google Cloud credentials
  - How to add test users to OAuth consent screen
  - Any other environment variables needed
  - Known limitations

### 3. Loom Video (15-20 minutes)

Record yourself covering:

**Part 1: Demo (5-7 min)**
- Sign in with your Google account
- Request a meeting with another participant
- Show the participant invitation flow
- Have the participant connect (use a second Google account)
- Show availability being checked across both calendars
- Book a meeting and show it appear on both calendars
- Demonstrate an edge case (no availability, modification, etc.)

**Part 2: Architecture (5-7 min)**
- Tech stack choices and why
- How you structured the agent logic
- How you handle multi-user OAuth
- How state flows through the system (especially the async participant connection)
- How you store/manage calendar tokens

**Part 3: Decisions & Tradeoffs (5-7 min)**
- Hardest design decisions you made
- What you'd do differently with more time
- Where you used AI assistance and where you didn't
- What would break first under scale
- How you'd add support for recurring meetings or Outlook calendars

---

## Time Expectation

We expect this to take **5-7 hours** for a working solution. The Google OAuth setup adds overhead compared to a mocked solution, but real integration is the point.

**What "done" looks like:**
- User can authenticate with Google
- User can request a meeting with 1-2 other participants
- Participants can connect their calendars via invite link
- System finds real availability across connected calendars
- Meeting is created on all connected calendars
- Core conversation flows work (schedule, check status, cancel)
- 1-2 edge cases handled thoughtfully

---

## Evaluation Criteria

| Dimension | Weight | What We're Looking For |
|-----------|--------|------------------------|
| **Integration Quality** | 25% | Does the Google Calendar integration actually work? Multi-user OAuth handled? |
| **Agent Design** | 25% | Is the agent logic well-structured? Does it handle the async nature well? |
| **Product Thinking** | 25% | Does it feel good to use? Is the participant flow clear? Edge cases handled? |
| **Communication** | 25% | Can you explain your decisions? Do you understand the tradeoffs? |

---

## Questions?

If anything is genuinely unclear, email us. We're happy to clarify requirements but won't give hints on design decisions—those are part of what we're evaluating.

---

## Internal Evaluation Notes

*This section is for internal use only—not shared with candidates.*

### What This Tests

**Primary signals:**
- Real API integration (OAuth, multi-user, token management)
- Agent design (tool use, state management, async flows)
- Handling complexity (multi-party, async participant connection)
- Product sense (is the participant flow clear and usable?)

**Hidden complexity:**
- Multi-user OAuth is significantly harder than single-user
- "Waiting for participants" state machine
- Timezone handling across multiple users
- What happens when someone revokes access mid-scheduling?
- Conversation context when async events happen

### Why Real Integration Matters

A mocked solution tests agent design but not:
- Ability to read and work with real API documentation
- Handling OAuth flows (which they'll do constantly on the job)
- Dealing with real-world API quirks and error handling
- Production thinking vs. demo thinking

### Red Flags

| Red Flag | What It Suggests |
|----------|------------------|
| OAuth doesn't actually work | Didn't test end-to-end |
| Only single-user OAuth | Missed the multi-party requirement |
| Can't explain token management | Doesn't understand OAuth |
| No handling of "waiting for participants" | Missed async complexity |
| Perfect solution, can't explain internals | Over-relied on AI |
| Participant flow is confusing | Poor product thinking |

### Follow-Up Questions (For Live Call)

- "Walk me through what happens when a participant's OAuth token expires."
- "What if Alice and Bob have zero overlapping availability?"
- "How would you add support for recurring meetings?"
- "What happens if someone revokes calendar access mid-conversation?"
- "How would you add Outlook calendar support?"
- "Walk me through what happens when two users try to book the same slot with the same participant."
- "How would you handle a participant who's in a very different timezone (16 hour difference)?"
