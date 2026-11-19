# GitHub-এ আপলোড ও ৩ সিস্টেমের অ্যাপ বানানোর গাইড

গেমটা প্রথমে Python কোড হিসেবে আছে। GitHub নিজেই (ফ্রিতে) Windows, macOS ও Linux-এর অ্যাপ বানিয়ে দেবে — আপনার কম্পিউটারে কিছু বানাতে হবে না।

## ধাপ ১ - রিপোজিটরি বানান
1. github.com-এ গিয়ে **New repository** চাপুন, নাম দিন `typestrike`, **Public** রাখুন, Create করুন।
2. এই zip খুলে ভেতরের **সব ফাইল ও ফোল্ডার** (লুকানো `.github` ফোল্ডারসহ) রিপোজিটরিতে আপলোড করুন।
   সহজ উপায় (টার্মিনাল / Git Bash):
   ```
   cd typestrike
   git init
   git add .
   git commit -m "TypeStrike first version"
   git branch -M main
   git remote add origin https://github.com/আপনার-ইউজারনেম/typestrike.git
   git push -u origin main
   ```
   (ব্রাউজারে "Upload files" দিয়ে টেনে আনলে `.github` ফোল্ডারটা অনেক সময় বাদ পড়ে - তাই Git ব্যবহার করাই ভালো।)

## ধাপ ২ - অ্যাপ বানান (Release)
```
git tag v1.0.0
git push origin v1.0.0
```
এরপর রিপোজিটরির **Actions** ট্যাবে "Build apps" চলবে (প্রায় ১০-২০ মিনিট)। শেষ হলে **Releases** পেজে তিনটা ফাইল পাবেন:
- `TypeStrike-Windows.exe`
- `TypeStrike-macOS.zip`
- `TypeStrike-Linux.tar.gz`

যে কেউ ওই পেজ থেকে নিজের সিস্টেমের ফাইলটা ডাউনলোড করে খেলতে পারবে। আপনি Releases পেজের লিংক বন্ধুদের পাঠাতে পারেন।

## আপডেট দিলে
কোড বদলে `git push` করুন, তারপর নতুন ট্যাগ দিন: `git tag v1.1.0 && git push origin v1.1.0`।

## সতর্কতা (সৎ কথা)
- অ্যাপগুলো GitHub-এর সার্ভারে প্রথমবার বানানো হবে। আমি এই পরিবেশে PyInstaller চালাতে পারিনি, তাই বিল্ড ফেল করলে Actions ট্যাবের লগ আমাকে দেখান - আমি ঠিক করে দেব।
- Windows ও macOS অ্যাপ "সাইন করা" নয়, তাই প্রথমবার সতর্কতা আসবে (README-তে কীভাবে খুলতে হবে লেখা আছে)।
- macOS বিল্ড শুধু Apple Silicon (M1/M2/M3...) Mac-এ চলবে। Intel Mac-এ `python3 typestrike.py` দিয়ে চালাতে হবে।
- Linux-এ সাউন্ডের জন্য `paplay`/`aplay` লাগে।
