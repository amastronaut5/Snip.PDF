<div align="center">
<img width="480" height="480" alt="LOGO1" src="https://github.com/user-attachments/assets/b90545f6-198f-47ce-a14c-fb1c610f55e6" />

# SnipPDF

### Stop collecting screenshots.

### Start building documents.

<br>

<p>
Capture screenshots continuously.<br>
Arrange them instantly.<br>
Export a PDF when you're done.
</p>

<br>

<img src="assets/hero.gif" width="100%"/>

<br>

![Windows](https://img.shields.io/badge/Windows-10%2F11-black?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.12+-black?style=for-the-badge)
![PyQt6](https://img.shields.io/badge/PyQt6-black?style=for-the-badge)

</div>

---

# Most screenshot workflows are broken.

You capture something.

Then something else.

Then something important.

Then twenty more things.

And suddenly:

```text
Screenshot (1).png
Screenshot (2).png
Screenshot (3).png
Screenshot (18).png
Screenshot (Final).png
Screenshot (Final_Final).png
```

Now you're managing files instead of ideas.

---

# SnipPDF changes the workflow.

```text
Capture
   ↓
Capture More
   ↓
Arrange
   ↓
Export PDF
```

No upload step.

No converter websites.

No temporary image chaos.

No friction.

---

# Built for people who think visually.

<table>
<tr>
<td align="center" width="25%">

### 📚

Students

</td>
<td align="center" width="25%">

### 🔬

Researchers

</td>
<td align="center" width="25%">

### 💻

Developers

</td>
<td align="center" width="25%">

### 📝

Documentation

</td>
</tr>
</table>

---

# Experience

<p align="center">
<img src="assets/workspace.png" width="95%">
</p>

<p align="center">
<i>Capture. Organize. Export.</i>
</p>

---

# Architecture

Not file based.

Session based.

```text
┌────────────────────┐
│ Screenshot Capture │
└──────────┬─────────┘
           │
           ▼
┌────────────────────┐
│ Memory Stack       │
└──────────┬─────────┘
           │
           ▼
┌────────────────────┐
│ Page Workspace     │
└──────────┬─────────┘
           │
           ▼
┌────────────────────┐
│ PDF Generation     │
└────────────────────┘
```

Everything remains in memory until export.

Fast.

Clean.

Predictable.

---

# Features

### Multi-Capture Sessions

Build an entire document from screenshots without leaving the application.

### Page Management

Reorder pages before export.

Remove mistakes instantly.

### In-Memory Processing

No temporary image clutter.

No unnecessary disk operations.

### Modern Desktop Interface

Built with PyQt6.

Focused on speed and clarity.

### One-Click Export

Generate a complete PDF from your session in seconds.

---

# Installation

## Download

```text
Releases
    ↓
Latest Version
    ↓
SnipPDF.exe
```

Run:

```text
Right Click
    ↓
Run As Administrator
```

Done.

---

## Build From Source

```bash
git clone https://github.com/YOUR_USERNAME/SnipPDF.git

cd SnipPDF

pip install -r requirements.txt

python main.py
```

---

# Roadmap

* [x] Multi-Screenshot Sessions
* [x] PDF Export
* [x] Page Reordering
* [x] Dark Interface

### Coming Next

* [ ] OCR
* [ ] Searchable PDFs
* [ ] Session Recovery
* [ ] DOCX Export
* [ ] Cloud Sync

---

# Philosophy

Good software removes steps.

Converting screenshots into a PDF shouldn't require:

* saving twenty files
* opening converter websites
* uploading everything again
* downloading the result

It should feel obvious.

SnipPDF was built around that idea.

---

<div align="center">

### Capture less friction.

### Create more documents.

⭐ Star the repository if it saved you time.

</div>
