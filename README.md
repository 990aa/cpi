 # SkillSwap Campus Demo

 A small, dependency-free demo of the SkillSwap peer learning exchange. Profiles and uploaded demo evidence are stored locally in `data/`, so two people can open the same forwarded port and see the same campus.

 ## Run with uv

 ```powershell
 uv run cpi
 ```

 Open `http://localhost:8000`. In VS Code, forward port `8000` and share the forwarded URL.

 The demo includes:

 - First-time registration with name, email, password, course, year, intro, phone, and skills
 - Login for returning users
 - Local student ID upload for verification
 - Local project or portfolio upload for skill showcase
 - Connection requests are locked until the current user has a verified ID and at least one project
 - For the demo, an image or PDF named exactly `id` is automatically verified; other ID filenames show admin verification pending
 - IDs are private; project files are viewable from other students' profile cards
 - Seeded campus profiles with teach/learn skill matching
 - Ten seeded student profiles with dummy portfolio previews
 - Skill search across names, courses, teach skills, and learn skills
 - Connect requests and accept/skip actions
 - Profile editing
 - Email links for contacting accepted connections

 The three seeded demo accounts are `dheeraj@campus.edu`, `swara@campus.edu`, and `mani@campus.edu`, all with password `demo`. New registrations are saved in `data/skillswap.json`; uploaded files are saved in `data/uploads/`.