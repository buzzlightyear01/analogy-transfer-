# یادداشت نسخهٔ مقاله

فایل اصلی: `acl_latex.tex`، در حالت ناشناس `review` قالب رسمی ACL.

## تطبیق فصل‌ها با بخش‌های مقاله

- فصل ۱ ← Introduction
- فصل ۲ ← Theoretical Foundations and Related Work
- فصل ۳ ← Research Method؛ شامل هر سه فاز و چارچوب چهارمرحله‌ای
- فصل ۴ ← Results and Analysis؛ با ترتیب سه فاز پایان‌نامه
- فصل ۵ ← Discussion and Conclusion؛ از نتایج فصل چهارم نوشته شده، چون فصل پنجم پایان‌نامه هنوز متن آموزشی قالب بود.

Limitations و Ethical Considerations جدا از متن اصلی‌اند. پیوست بعد از منابع قرار دارد. فایل سبک `acl.sty` تغییر نکرده است. نسخهٔ نمونهٔ اولیه در `reference/acl_template_original.tex` نگه داشته شده است.

## حدود شواهد حفظ‌شده

- فاز اول: GPQA Main؛ ۴۴۸ پاسخ ثبت‌شده در هر شرط لاما، کوعن و میسترال. تعداد رکوردهای جما بسته به شرط ۴۳۵ تا ۴۴۷ است؛ اختلاف کلی آن را نباید مقایسهٔ کاملاً همتای سؤال‌به‌سؤال تلقی کرد.
- فاز دوم: ۱۰۳ سؤال؛ ۶۱ معمای قتل، ۲۱ جای‌گذاری اشیا و ۲۱ تخصیص نقش. چهار حالت روی همان مقصدها، با ارائه/حذف صرفاً پاسخ مبدأ. آزمون پاسخ صحیح در برابر پاسخ غلط گزارش نشده است.
- فاز سوم: واقعاً ۱۰۰ سؤال در هر مجموعه‌داده. شمارش‌های برخی نمودارهای پایان‌نامه دو برابر نمایش داده شده‌اند؛ در مقاله شمارش واقعی استفاده شده است.
- اصلاح upstream اوراکل‌محور از عملکرد مستقل مدل جداست. اصلاح پاسخ نهایی به‌عنوان rescue شمرده نشده است.
- نتایج مدل دوم فاز سوم هنوز کامل نیست و وارد مقاله نشده است.
- منابع از کتابنامهٔ پایان‌نامه انتخاب شده‌اند؛ برای منابع جدید، دقت فراداده و ادعاها قبل از ارسال نهایی باید با اصل مقاله بازبینی شود.
- بازنویسی انگلیسی و LaTeX با کمک هوش مصنوعی انجام شده و در بخش Ethical Considerations ذکر شده است؛ فرم Responsible NLP باید متناسب با استفادهٔ واقعی تکمیل شود.

## منابع عددی

- `../tehran-thesis-master/tex/chapter4.tex`
- `../tehran-thesis-master/output/figures/chapter4/selected_phase1/source_values.json`
- `../output/phase1_analogy_pies/summary.json`
- `../tehran-thesis-master/output/phase1_cot_transitions/audit.json`
- `../tehran-thesis-master/output/phase2_chart_options/values.json`
- `../tehran-thesis-master/output/figures/chapter4/selected_phase2/llama_answer_positions_audit.json`
- `../result_audit/real_chart_atlas/canonical/observed_stage_flow_data.csv`

## ساخت

روی این دستگاه:

```sh
PATH=/Library/TeX/texbin:$PATH latexmk -pdf -interaction=nonstopmode -halt-on-error -outdir=build acl_latex.tex
```

در Overleaf، فایل اصلی `acl_latex.tex` و کامپایلر pdfLaTeX انتخاب شود. همهٔ فایل‌های sections، figures، custom.bib، acl.sty و acl_natbib.bst لازم‌اند.

## نتیجهٔ بررسی خروجی

متن اصلی ۸ صفحه و PDF کامل ۱۱ صفحه است. Limitations از صفحهٔ ۹ شروع می‌شود. هیچ ارجاع تعریف‌نشده یا خطای overfull در لاگ نهایی وجود ندارد. جدول‌ها و شکل‌ها در PDF رندر و بازبینی شدند.
