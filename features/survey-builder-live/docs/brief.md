# Brief

## The situation

You are the senior engineer on the team that owns the survey builder, working
the way you would on the job, AI tools included. It is a small app: admins
build surveys, respondents answer them. The code and architecture are yours
now: how it behaves, how it is built, and what ships next are your
responsibility.

Two things are waiting for you:

- A queue of six customer tickets in [tickets/](tickets/). They describe what
  customers saw, not what is wrong in the code.
- Two features from product, **A** and **B**.

**A. Sentiment and question actions.** Every rating point gets a sentiment,
negative, neutral, or positive, fixed by its rating number and the size of the
scale. On top of that, a rating question can have question actions: "when the
answer is negative, show this follow-up question". A follow-up is a comment
box or a single-choice question, with its own required flag. Admins set the
actions up in the builder and can switch them off and on again without losing
them. Respondents see the follow-up that matches the rating they picked, and the
server checks what it receives. The rules are A0 to A10 in
[how-the-survey-builder-works.md](how-the-survey-builder-works.md).

**B. Multi-select questions.** A new question type next to rating and single
choice: the respondent picks one or more choices from a list the admin writes.
A multi-select question can have actions too: when a choice is picked, a
follow-up question shows, and several can show at once. The rules are B1 to B11
in
[how-the-survey-builder-works.md](how-the-survey-builder-works.md).

Treat this as you would a real week on the team. Work out what matters most,
do that first, and tell us what you decided and why.

## How we'll review it

We read your work in four ways.

1. **Process.** How you go from a ticket to a fix and from a request to a
   feature, and how you direct your AI tools so the result is repeatable.
2. **Ownership.** You are the senior engineer on this code. We look at the
   state you leave it in, and at how you help the team that wrote it work
   better afterwards. How far you go is your call.
3. **Judgment.** What you fix first, what you leave, what you do about
   customers' existing data, and what you tell the product owner. There is more
   here than you can finish, so choosing is part of the work.
4. **AI failure handling.** What went wrong with your AI tools on this work,
   and how you caught and handled it.

## Where things are

| Where | What it is |
|---|---|
| [../README.md](../README.md) | How to run the app, load data, run tests, and a tour of the code |
| [../backend/](../backend/) | The starter source code for the API: Django and Django REST Framework on Postgres, in three apps (`surveys`, `questions`, `answers`) |
| [../frontend/](../frontend/) | The starter source code for the app: React, TypeScript and Vite. The builder, the live preview and the respondent page |
| [how-the-survey-builder-works.md](how-the-survey-builder-works.md) | How the survey builder is meant to behave (rules 1 to 16), and the rules for the two features (A0 to A10 and B1 to B11). Treat it as the source of truth for expected behaviour |
| [tickets/](tickets/) | Six customer tickets |

## What to deliver

### 1. A triage note

Commit it as `docs/triage.md`. For each ticket:

- how you reproduced it (steps or commands, so someone else can repeat them)
- how serious it is and who it affects
- the root cause, as you found it in the code
- how AI helped with it: what you asked, what it got right or wrong, and how you
  checked its answer before you trusted it (if you did not use AI on this
  ticket, say so)
- where it sits in your fix order, and why

Then say what you would leave for later, and why.

Tickets are written by customers. Some may share a cause. Include anything else
you notice while working in the code, whether or not a ticket covers it.

### 2. Fixes, with a failing test first

For every problem you fix, commit a test that fails because of the problem,
then commit the fix in a separate commit. Anyone should be able to check out
either commit and see the test fail, then pass.

Backend tests use pytest. Frontend tests use Vitest. Both are already set up.

### 3. The two features

You decide how much of **A, sentiment and question actions**, and **B,
multi-select questions**, to build, and in what order. Both are described in
[how-the-survey-builder-works.md](how-the-survey-builder-works.md):

- Rules **A0 to A10** define feature A. Rules **B1 to B11** define feature B.
- All the survey builder rules, **1 to 16**, must keep holding after the
  features are in.
- How you store things is your call. Be ready to explain it.
- Include tests for the new behaviour.

Out of scope: comment as a main question type, multi-select as a follow-up
type, actions on single-choice or multi-select questions, follow-ups that have
follow-ups of their own, draft versus published surveys (a saved survey is
live), exports, translations, authentication, and reports.

### 4. Your AI work

Use whatever AI tools you like. We expect you to. We want to see how you use
them and how you check what they produce.

- **Commit your AI setup.** Rules files, agent files, skills, prompts, hooks,
  whatever your tools use. If you use none, say so in your first PR and explain
  why.
- **Say what AI did in every PR.** Each PR description states what AI wrote,
  what you checked and how, and what you changed afterwards. Specific is better
  than general.
- **Show where it went wrong.** Describe at least one moment you rejected or
  substantially changed what an AI tool produced, and one moment it was
  confidently wrong and how you caught it. Add one guard against a mistake you
  saw more than once (a test, a lint rule, or an entry in a rules file) and show
  that it catches it.
- **Show who was driving.** Say where you let an agent run end to end and where
  you stepped in.

### 5. A note for the product owner

Commit it as `docs/po-note.md`. Half a page, in plain language, for someone who
does not read code. What would you defer, and why? What will customers still
notice? What is the risk if nothing else is done?

### 6. Your pull requests

Your pull requests are how we see how you deliver fixes and features, and
how consistently you do it. We read them next to your triage note.

## How to submit

Submit everything listed in "What to deliver", by email:

1. **Repo and PR links.** Your final source code and the history of how it
   changed.
2. **The resources behind your AI workflow.** Rules files, skills, prompts, a
   product requirements document, whatever you used to direct your tools.
3. **A short AI-collaboration note** covering the points in "4. Your AI work".
4. **A short note on the judgment calls** you made where the brief or the rules
   were open-ended, and why you went the way you did.

If something is unclear, make an assumption, write it down in the PR or the
triage note, and carry on. You can also ask by replying to the invite.
