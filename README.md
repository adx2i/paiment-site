# paiment.cc website

Static site with a PHP lead form and a private lead tracker, hosted on Namecheap shared hosting.

- `index.html`, `thanks.html`, `assets/`: the public pages.
- `lead.php`: saves each form submission to `~/paiment-data/leads.jsonl` (outside the web root) and emails a notification.
- `admin/`: lead tracker. Must be password protected with cPanel Directory Privacy.
- `.cpanel.yml`: copies the site into `public_html` when deployed from cPanel's Git Version Control.
- `_source/`: design source and build script used to generate `index.html`. Not deployed.

No lead data or credentials are stored in this repository.
