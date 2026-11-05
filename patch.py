import re
B = 'app/src/main/java/com/kurdish/manhwareal/'

def rd(n):
    return open(B + n, encoding='utf-8').read()

def wr(n, s):
    open(B + n, 'w', encoding='utf-8').write(s)

def sub1(s, old, new):
    assert s.count(old) == 1, 'anchor not found exactly once: ' + old[:70]
    return s.replace(old, new)

# ---------- Chapter.kt ----------
s = rd('Chapter.kt')
s = sub1(s, 'bytes: ByteArray, img: Img, ratio: Float): List<ChItem> {',
         'bytes: ByteArray, img: Img, ratio: Float, pass: Int = 1): List<ChItem> {')
s = sub1(s, 'while (sw / (sample * 2) >= 700) sample *= 2',
         'val target = if (pass == 1) 700 else 1000\n        while (sw / (sample * 2) >= target) sample *= 2')
s = sub1(s, 'val k1 = minOf(k0 + tileSrc, sh)',
         'val step = if (pass == 2 && k0 == 0) tileSrc / 2 else tileSrc\n            val k1 = minOf(k0 + step, sh)')
wr('Chapter.kt', s)

# ---------- Web.kt ----------
s = rd('Web.kt')
s = sub1(s, 'private var chGemDone = 0',
         'private var chGemDone = 0\n'
         '    private var chPass = 1\n'
         '    private val chImgList = ArrayList<Chapter.Img>()\n'
         '    private var chRatio = 1f\n'
         '    private var chUa = ""\n'
         '    private var chRef = ""')
s = sub1(s, 'private fun chCancel() {',
         'private fun chCancel() {\n        chPass = 1\n        chImgList.clear()')
s = sub1(s, 'chImgTotal = arr.length()',
         'chImgTotal = arr.length()\n'
         '            chPass = 1\n'
         '            chImgList.clear()\n'
         '            for (j in 0 until arr.length()) {\n'
         '                val oo = arr.getJSONObject(j)\n'
         '                chImgList.add(Chapter.Img(oo.getString("src"), oo.getDouble("x").toFloat(), oo.getDouble("y").toFloat(), oo.getDouble("w").toFloat(), oo.getDouble("h").toFloat()))\n'
         '            }\n'
         '            chRatio = ratio\n'
         '            chUa = ua\n'
         '            chRef = ref')
s = sub1(s, 'if (Fast.isJunk(ci.text)) continue',
         'if (Fast.isJunk(ci.text)) continue\n            if (chPass == 2 && chDup(ci)) continue')
s = sub1(s, 'private fun chOnImage(gen: Int, items: List<ChItem>) {',
         '''private fun chDup(ci: ChItem): Boolean {
        val a1 = ci.px
        val b1 = ci.py
        val a2 = ci.px + ci.w
        val b2 = ci.py + ci.h
        for (o in chItems) {
            val ix = minOf(a2, o.px + o.w) - maxOf(a1, o.px)
            val iy = minOf(b2, o.py + o.h) - maxOf(b1, o.py)
            if (ix > 0 && iy > 0) {
                val inter = ix.toLong() * iy
                val small = minOf(ci.w.toLong() * ci.h, o.w.toLong() * o.h)
                if (small > 0 && inter * 100 > small * 30) return true
            }
        }
        return false
    }

    private fun chLaunch2(gen: Int) {
        chPass = 2
        chImgTotal = chImgList.size
        chImgDone = 0
        val cm = CookieManager.getInstance()
        val ratio = chRatio
        val ua = chUa
        val ref = chRef
        chProgress()
        for (img in ArrayList(chImgList)) {
            Chapter.workers.execute {
                val items: List<ChItem> = try {
                    if (gen != chGen) {
                        emptyList()
                    } else {
                        val bytes = Chapter.fetch(img.src, ref, ua, cm.getCookie(img.src))
                        if (bytes == null || gen != chGen) emptyList() else Chapter.ocr(recognizer, bytes, img, ratio, 2)
                    }
                } catch (e: Throwable) {
                    emptyList()
                }
                handler.post { chOnImage(gen, items) }
            }
        }
    }

    private fun chOnImage(gen: Int, items: List<ChItem>) {''')
s = sub1(s, 'private fun chProgress() {',
         'private fun chProgress() {\n'
         '        if (chState != 0 && chPass == 1 && chImgList.isNotEmpty() && chImgDone >= chImgTotal) {\n'
         '            chLaunch2(chGen)\n'
         '            return\n'
         '        }')
s = sub1(s, '+ chImgDone + "/" + chImgTotal',
         '+ "[" + chPass + "/2] " + chImgDone + "/" + chImgTotal')
wr('Web.kt', s)

# ---------- Auth.kt ----------
s = rd('Auth.kt')
s = sub1(s, 'm.contains("HTTP 409") -> warn(act, u, cb)',
         'm.contains("HTTP 409") -> warn(act, u, cb, m.substringAfter("\\"count\\":", "").takeWhile { it.isDigit() }.ifEmpty { "30" })')
s = sub1(s, 'private fun warn(act: Activity, u: String, cb: (Boolean) -> Unit) {',
         'private fun warn(act: Activity, u: String, cb: (Boolean) -> Unit, count: String = "30") {')
i = s.index('private fun limit(')
a, b = s[:i], s[i:]
def one(pattern, text, repl):
    out, n = re.subn(pattern, lambda m: repl, text, count=1, flags=re.M)
    assert n == 1, 'pattern not found: ' + pattern
    return out
a = one(r'\.setTitle\(".*"\)$', a, '.setTitle(count + " چاپتەر! 😄")')
a = one(r'\.setMessage\(".*"\)$', a,
        r'.setMessage(count + " چاپتەرت خوێندەوە! ئەگەر دەتەوێت بەردەوام بیت، چاوەکانت و خەوەکەت بەلاوە گرنگ نین؟ 😄\n\nبۆ ئەمڕۆ تا ٣٥٠ چاپتەر ڕێگەپێدراوە، و هەر ٣٠ چاپتەر جارێک ئاگادارت دەکەمەوە.")')
b = one(r'\.setTitle\(".*"\)$', b, '.setTitle("٣٥٠ چاپتەر! 🛑")')
b = one(r'\.setMessage\(".*"\)$', b,
        r'.setMessage("٣٥٠ چاپتەرت خوێندەوە! خۆ چاوەکانت نەتوێنەوە؟ 😅\n\nبۆ ئەمڕۆ تەواو بوو، سبەینێ بگەڕێوە و بەردەوام به.")')
wr('Auth.kt', a + b)
print('patch OK')
