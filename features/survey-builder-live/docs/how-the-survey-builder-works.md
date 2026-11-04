# How the survey builder works

This document describes how the survey builder is meant to behave. Treat it as
the product definition: if the app and this document disagree, the document is
right. The rule numbers are stable, so you can refer to them in tickets, tests,
and PRs.

| Part | Rules | Where they stand |
|---|---|---|
| The survey builder | 1 to 16 | How the builder is meant to behave today, whatever the code does at the moment. |
| Homework A: sentiment and question actions | A0 to A10 | New work. The app does not do any of this yet. |
| Homework B: multi-select questions | B1 to B11 | New work. The app does not do any of this yet. |

Rules 1 to 16 must still hold once you have added A and B.

## Terms

| Term | Meaning |
|---|---|
| **Survey** | A name and an ordered list of questions. |
| **Question** | Text, a type, a required flag, and a display order. |
| **Rating question** | A scale of 2 to 5 points. Each point has a **rating number** (1 is the lowest) and a label. |
| **Single-choice question** | The respondent picks one choice from a list the admin writes. |
| **Multi-select question** | *(Homework B.)* The respondent picks one or more choices from a list the admin writes. |
| **Choice** | One option of a single-choice or multi-select question. It has a stable identity, a label, and a display order. Identity and order are separate: moving a choice changes where it shows, never what it is. |
| **Direction** | A display option of a rating question: lowest first (1 to 5) or highest first (5 to 1). Display only. |
| **Answer count** | The number the builder shows next to each choice and each rating point: how many answers picked it. |
| **Archived** | What happens to an item the admin deletes. It no longer shows in the builder or to respondents, but it stays stored, and the answers given against it stay readable. |
| **Sentiment** | *(Homework A.)* `negative`, `neutral`, or `positive`. Every rating point has one, fixed by its rating number and the scale size. |
| **Question action** | *(Homework A.)* A rule on a rating question: "Answer is *sentiment*: show a follow-up". On a multi-select question (homework B) it is "*this choice* is picked: show a follow-up". |
| **Follow-up question** | *(Homework A.)* The question an action shows: a comment or a single choice. |
| **Actions toggle** | *(Homework A.)* Turns a question's actions on or off. |

## Rating scales

A rating question has one scale of 2 to 5 points. These are the default labels
for each size, from point 1 up to the last point. Admins can edit them.

| Points | Labels, 1 to n |
|---|---|
| 5 | Terrible, Bad, Okay, Good, Great |
| 4 | Bad, Poor, Good, Great |
| 3 | Bad, Okay, Good |
| 2 | Bad, Good |

## Rules: the survey builder

### Survey and saving

1. A new survey starts with no questions. It cannot be saved until it has at
   least one question. The server enforces this too, not only the browser.
2. Saving is **one request for the whole survey**: questions, choices, order,
   and settings together. There is no save per question. A question or option
   that was saved before stays the same item after every save, wherever it now
   sits in the list: new items are added, items that are no longer sent are
   archived, and existing items are updated.
3. Once saved, the survey is **live**. Respondents can answer it at any time,
   and the respondent page always shows the latest saved version.
4. Every edit shows in the live preview at once, without saving or refreshing.

### Questions

5. The question types are **rating** and **single choice**. (Homework B adds
   multi-select.)
6. Each question has a **required** flag. A question that is not required can
   be skipped. A required question must be answered, and the server enforces
   this too, not only the browser.
7. Questions can be added, deleted, and reordered.

### Single choice

8. The admin can add, rename, delete, and reorder choices. Reordering changes
   display only.

### Rating

9. A rating question has one scale of **2 to 5 points**.
10. The **rating number** (1 to n) is the point's identity. An answer stores
    the rating number that was picked.
11. Rating points have no sentiment before homework A. Sentiment arrives with
    rule A0.
12. Labels are editable. Each scale size has default labels (table above).
13. **Direction** changes display only. Picking a point saves its rating
    number, whichever direction is shown.

### After answers exist

14. **Deleting never deletes past answers**: not for a question, not for a
    choice, and, with homework A, not for an action or a follow-up. Deleted
    items are archived and stay readable.
15. **Answers keep what the respondent saw.** Any edit made after answers exist
    (question text, choice or point labels, scale size, type) does not change
    the meaning of old answers. An old answer still shows the question, the
    labels, and the scale it was given against.
16. Reordering never moves answers onto another question or choice.

## Rules: homework A, sentiment and question actions

New work. These rules build on rules 1 to 16.

- **A0.** Every rating point has a **sentiment**, fixed by its rating number
  and the scale size. The admin cannot change it. The builder, the preview, and
  the respondent page show it (for example as the point's colour).

  | Points | 1 | 2 | 3 | 4 | 5 |
  |---|---|---|---|---|---|
  | **5** | negative | negative | neutral | positive | positive |
  | **4** | negative | negative | positive | positive | |
  | **3** | negative | neutral | positive | | |
  | **2** | negative | positive | | | |

  The rule for every size: the lower half is negative, the upper half is
  positive, and the middle point of an odd scale is neutral.
- **A1.** Actions exist on rating questions. (Homework B adds them to
  multi-select questions, rule B6.)
- **A2.** A question has at most one action per sentiment, so a rating triggers
  at most one follow-up.
- **A3.** Each action owns exactly one follow-up question, of type **comment**
  or **single choice**. A single-choice follow-up has its own choices, which
  follow rule 8.
- **A4.** A follow-up appears right after its rating question, only when the
  picked point's sentiment matches an action and actions are on. Direction
  (rule 13) never changes which follow-up appears.
- **A5.** If the respondent changes the rating, the follow-up changes to match.
  The answer to a follow-up that is no longer shown is dropped.
- **A6.** A follow-up has its own required flag. A required follow-up must be
  answered when it is shown, and is never required when it is not shown.
- **A7.** The **actions toggle**: off hides the actions from respondents and
  keeps them; on brings them back unchanged.
- **A8.** The server re-checks A4 to A6 on submit. It accepts a follow-up
  answer only if the rating in the same response triggers it.
- **A9.** Changing the scale size changes each point's sentiment (rule A0), so
  which points trigger which action changes at once. Old answers keep their
  meaning (rule 15).
- **A10.** Actions and follow-ups are saved as part of the whole survey
  (rule 2) and follow rules 14 to 16.

## Rules: homework B, multi-select questions

New work. These rules build on rules 1 to 16.

- **B1.** A new main question type. It is **not** a follow-up type.
- **B2.** The respondent picks one or more choices. Required means at least one
  pick.
- **B3.** Choices follow rule 8.
- **B4.** Rules 2 and 14 to 16 apply.
- **B5.** No minimum or maximum number of picks, beyond rule B2.
- **B6.** Multi-select questions can have actions, as rating questions can
  (rule A1). An action on a multi-select question is "*this choice* is picked:
  show a follow-up". Each action is tied to one choice.
- **B7.** A choice has at most one action. Each action owns exactly one
  follow-up question, a comment or a single choice (rule A3).
- **B8.** The respondent can pick several choices, so several follow-ups can be
  due at once. Each shows right after the question, in the order of its choice
  in the list. Every follow-up whose choice is picked shows, not only one.
- **B9.** If the respondent un-picks a choice, its follow-up disappears and its
  answer is dropped, as in rule A5.
- **B10.** Rules A6, A7, A8 and A10 apply to these actions too. On submit the
  server accepts a follow-up answer only if the picks in the same response
  trigger it.
- **B11.** Moving a choice never changes which action belongs to it (rule 16).
  Removing a choice archives its action and follow-up, and never deletes
  answers (rule 14).

## Worked example

Survey **"Support CSAT"**: question 1 is a rating, 5 points, lowest first,
required. Question 2 is a single choice, "How did you contact us?" (Phone,
Email, Chat), not required.

| Respondent does | What is saved |
|---|---|
| Picks Great (5) on question 1, skips question 2 | Question 1 = 5. Question 2 is skipped, which is allowed. |
| Skips question 1 | Refused: question 1 is required, in the browser and on the server. |
| Picks Great with direction "highest first" | Question 1 = 5, the same as with lowest first. |

The admin then edits the survey after answers exist:

| Admin edit, then save | Old answers |
|---|---|
| Moves Email above Phone | Still counted under the same labels. |
| Deletes question 2 | Question 2 is archived. Its answers stay readable. No other question gets them. |
| Renames "Chat" to "Live chat" | Old answers still show "Chat". New answers show "Live chat". |
| Changes question 1 from 5 to 3 points | Old answers keep their 5-point meaning: an old 3 is still "Okay, 3 out of 5". New answers use the 3-point scale. |

With homework A on question 1 (negative: comment "What went wrong?", required;
positive: single choice "What did you like?" with Speed and Friendliness):

| Respondent picks | Follow-up |
|---|---|
| Terrible (1) | "What went wrong?", which must be answered. |
| Okay (3) | None. |
| Great (5), then changes to Bad (2) | "What did you like?" disappears with its answer. "What went wrong?" shows. |
| Bad, with actions toggled off | None. The actions are kept for later. |

With homework B on a multi-select question "What did you use?" (Phone, Email,
Chat), with an action on Phone (comment "What went wrong on the call?",
required) and an action on Chat (single choice "Was the bot involved?"):

| Respondent picks | Follow-ups |
|---|---|
| Email | None. |
| Phone | "What went wrong on the call?", which must be answered. |
| Phone and Chat | Both, Phone's first, in the order of the choices. |
| Phone and Chat, then un-picks Phone | Phone's follow-up and its answer disappear. Chat's stays. |

## Data flow

```
Builder (left) --edits--> one shared state --> Live preview (right)
      |
      | save (whole survey, one request)
      v
Server --- add / update / archive, same items stay the same items, answers never move
      |
      +--- survey payload (latest saved version) ---> Respondent page
                                                          |
                                                          | submit (whole response)
                                                          v
                                         Server checks required (and A4 to A8, B8 to B10), then saves
```

The builder and the live preview read one shared state, so an edit shows in the
preview without a save or a refresh. Once a survey is saved it is live: the
respondent page loads the latest saved version.
