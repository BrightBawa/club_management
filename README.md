### Club Management

Foundation app for school clubs and activities in Frappe / ERPNext.

Implemented in this pass:

- app hooks and install-time role/workspace setup
- core clubs doctypes for settings, categories, clubs, member profiles, patron profiles, and memberships
- basic website helpers and public `/clubs` landing page

Next phases should add meetings, activities, events, projects, elections, attendance, and approvals.

### Public clubs website

The club, patron, and member pages use GCIHS colours, Roboto, responsive profile
layouts, rich biographies, and a full-height layout consistent with Sports.
The `/clubs` page shows a configurable formation notice until active clubs are
published. A Clubs link appears beside Sports in the website navigation.

Each profile form has **Additional Profile Details** and **Website Display
Options**. Enter the information, tick **Show … on Website**, and save to display
the selected detail. Empty values and unticked details are omitted from both
profiles and directories. Selected photos must be public images; private files
are never converted automatically.

- Clubs: mission, objectives, activities, achievements, membership requirements,
  meeting details, leadership, images, and an optional member roster.
- Patrons: designation, skills, qualifications, mentoring experience and approach,
  achievements, languages, and supervised clubs.
- Members: interests, skills, achievements, goals, contributions, optional school
  details, and approved club memberships and roles.

Keep a club in **Draft** while it is being formed. To publish it, set its status
to **Active**, tick **Publish on Website**, and select **Published** profile status.
Public member profiles additionally require **Public Member Profiles Enabled**
in Club Settings, public profile visibility, and active membership status.
Rosters use approved, active, current memberships and individually published
member profiles; both the club and member must opt into the affiliation display.
Draft and disabled profiles cannot be viewed anonymously through their routes.
