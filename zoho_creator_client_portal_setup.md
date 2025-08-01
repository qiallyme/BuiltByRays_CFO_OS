**Q, baby, YES.** Now you talkin' like the boss you are:

> 💡 “Let’s get *one damn thing working*, then we can evolve it.”

Say less. I got you. Here comes your **Zoho Creator Minimal Viable Client Portal (MVCP)**—aka *a working app today* that:

- ✅ Lists their files from WorkDrive
- ✅ Lets them upload stuff into their folder
- ✅ Feels like a real portal (mobile ready)
- ✅ Costs you *zero extra dollars*

---

## 🚀 LET’S BUILD IT: “Client Portal Lite” in Zoho Creator

---

### 🔧 STEP 1: **Structure Your Data**

#### ✨ Create 1 Form (call it `Client Uploads`)

Fields:

- **Client Email** (email type – used for login filter)
- **File Name** (single line)
- **Upload** (file upload)
- **Notes** (multi-line, optional)

> 🧠 Optional: Auto-fill `Created Time` + `Uploaded By` from system fields.

---

### 📁 STEP 2: **Link to WorkDrive Folders**

If you have a folder per client on WorkDrive:

1. Inside the form, add a **multi-line URL field** called `View My Files`.
2. Paste the link to their WorkDrive folder (set to "Anyone with the link can view").
3. If you want it slicker: add a workflow that generates the link based on email matching folder name. (We’ll do that later.)

---

### 👥 STEP 3: **Lock the Portal to Each Client**

Use **User Authentication + Client Email Filtering**:

- In Creator, go to:
  > `Users & Control > Portals` → Enable client login via email
- In the `Client Uploads` form view:
  > Add a filter: `Client Email = zoho.loginuserid`
- Boom: each client only sees their own uploads.

---

### 📱 STEP 4: **Design a Simple Page View**

Go to **Pages**, create a homepage like:

```
Welcome, [Client Email]!

📂 Your Files
[View My Files button]

⬆️ Upload a New Document
[Embed Client Uploads form]

📜 Upload History
[List view of Client Uploads, filtered to their email]
```

Use buttons or custom blocks to make it feel app-like.

---

### 📲 STEP 5: **Mobile App Feel**

Tell your client:

> “Click this link → Log in once → Tap ‘Add to Home Screen’ = It’s an app now.”

✅ Works on iPhone and Android\
✅ No need for App Store or installs

---

## 🔐 OPTIONAL (Future-You Checklist)

- Add checklist status (pending/reviewed)
- Add comment/chat thread per upload
- Tie into Zoho Flow for reminders/notifications
- Integrate Google Drive links if needed
- Upload directly to WorkDrive (advanced—uses API)

---

## 🧠 TL;DR: BUILD NOW CHECKLIST

1. ✅ Form: `Client Uploads`
2. ✅ Fields: Email, File Upload, File Name, Notes
3. ✅ Add public WorkDrive link field
4. ✅ Enable client portal login by email
5. ✅ Create filtered views so each client sees only theirs
6. ✅ Build one clean page with file link + upload zone
7. ✅ Share the portal URL + “add to home screen” trick

---

## 💥 Want It Faster?

Tell me:

- Do you already have client folder URLs?
- Want me to write the **Deluge rule** that autofills folder links?
- Need a homepage layout template?

I’ll type that all up real quick for you.\
You’re *one click away* from working, Q. Let’s hit publish.
