from generalFunctions import *
from ctypes import *
import sys, os, time, getopt, random
import subprocess, threading
import win32api, win32process, win32con, win32gui
import wx, sgf

##################################################

# 以下为 Zen7GTP 专用变量
booksgf = {}
values = []
mainpv = []
Strength = [10000, 1000000000]  # 新默认参数 -S 10000；原默认参数为颠倒，即 -S 10000+
strength = [1000000000, 1000000000, 10000]

Aparm = [1, 1000000000, 1000000000]
aparm = [0, 100]
bparm = [1000000000, 1000000000]
fparm = [3, 1.0]
gparm = [500, 0]
nparm = 10
pparm = 2
Qparm = [1000000000, 1.0]
rparm = [2, 500]
uparm = 0
vparm = 0  # 默认关闭控制台
Xparm = 1000000000
xparm = [100, 0.1]

human = False

###############################################


try:
    opts, args = getopt.getopt(
        sys.argv[1:],
        "ht:T:S:s:l:k:f:w:q:Q:r:b:p:x:X:u:g:v:n:A:a:H",
        ["help", "threads=", "maxtime=", "strength=", "logfile="],
    )
except getopt.GetoptError:
    help()
# if args != []: help()

for opt, arg in opts:
    if opt in ["-h", "--help"]:
        help()
    if opt in ["-t", "--threads"]:
        if not arg.isdigit() or int(arg) < 1:
            help()
        threads = int(arg)
        continue
    if opt in ["-T", "--maxtime"]:
        maxtime = float(arg)
        continue
    if opt in ["-S", "--strength"]:
        if len(arg.split(",")) == 1:
            if arg[-1] == "+":
                Strength = [1000000000, int(arg[:-1])]
            else:
                Strength = [int(arg), 1000000000]
            continue
        if len(arg.split(",")) == 2:
            S0, S1 = arg.split(",")
            if S1 == "" or S1[-1] != "+":
                help()
            Strength = [int(S0), int(S1[:-1])]
            continue
        help()
    if opt in ["-s"]:
        if len(arg.split(",")) == 2:
            s0, s1 = arg.split(",")
            if s1 == "":
                help()
            if s1[-1] == "+":
                strength = [int(s0), 1000000000, int(s1[:-1])]
            else:
                strength = [int(s0), int(s1), 1000000000]
            continue
        if len(arg.split(",")) == 3:
            s0, s1, s2 = arg.split(",")
            if s2 == "" or s2[-1] != "+":
                help()
            strength = [int(s0), int(s1), int(s2[:-1])]
            continue
        help()
    if opt in ["-l", "--logfile"]:
        logfile = arg
        continue
    if opt in ["-k"]:
        k1, k2 = arg.split(",")
        komi[1] = float(k1)
        komi[2] = float(k2)
        continue
    if opt in ["-f"]:
        f0, f1 = arg.split(",")
        fparm = [int(f0), float(f1)]
        continue
    if opt in ["-w"]:
        w0, w1 = arg.split(",")
        weight = [float(w0), float(w1)]
        continue
    if opt in ["-q"]:
        q0, q1 = arg.split(",")
        qparm = [int(q0), float(q1) * 1000]
        if qparm[0] < 0 or qparm[1] > 1000 or qparm[1] < 0:
            help()
        continue
    if opt in ["-Q"]:
        Q0, Q1 = arg.split(",")
        Qparm = [int(Q0), float(Q1)]
        if Qparm[0] < 0 or Qparm[1] > 1.0 or Qparm[1] < 0.0:
            help()
        continue
    if opt in ["-r"]:
        r0, r1 = arg.split(",")
        rparm = [int(r0), float(r1) * 1000]
        if rparm[0] < 2 or rparm[1] < 0 or rparm[1] > 1000:
            help()
        continue
    if opt in ["-b"]:
        if len(arg.split(",")) == 2:
            b0, b1 = arg.split(",")
            bparm = [int(b0), int(b1)]
            if bparm[0] < 0 or bparm[1] < 0:
                help()
        elif len(arg.split(",")) == 1:
            bparm = [int(arg), 1000000000]
            if bparm[0] < 0:
                help()
        else:
            help()
        continue
    if opt in ["-p"]:
        pparm = int(arg)
        if pparm < 0 or pparm > 4:
            help()
        continue
    if opt in ["-x"]:
        x0, x1 = arg.split(",")
        xparm = [int(x0), float(x1)]
        if xparm[0] < 2 or xparm[1] < 0 or xparm[1] > 1:
            help()
        continue
    if opt in ["-X"]:
        Xparm = int(arg)
        if Xparm < 0:
            help()
        continue
    if opt in ["-u"]:
        uparm = float(arg)
        if uparm < 0:
            help()
        continue
    if opt in ["-v"]:
        vparm = int(arg)
        if vparm < 0 or vparm > 3:
            help()
        continue
    if opt in ["-n"]:
        nparm = int(arg)
        if nparm < 1 or nparm > 10:
            help()
        continue
    if opt in ["-A"]:
        if len(arg.split(",")) == 3:
            A0, A1, A2 = arg.split(",")
            Aparm = [int(A0), int(A1), int(A2)]
            if Aparm[0] < 1 or Aparm[1] < Aparm[0] or Aparm[2] < 1:
                help()
        elif len(arg.split(",")) == 2:
            A0, A1 = arg.split(",")
            Aparm = [int(A0), int(A1), 1000000000]
            if Aparm[0] < 1 or Aparm[1] < Aparm[0]:
                help()
        elif len(arg.split(",")) == 1:
            Aparm = [int(arg), 1000000000, 1000000000]
            if Aparm[0] < 1:
                help()
        else:
            help()
        continue
    if opt in ["-H"]:
        human = True
        continue
    if opt in ["-g"]:
        g0, g1 = arg.split(",")
        gparm = [int(g0), int(g1)]
        if gparm[0] < 0 or gparm[1] < 0:
            help()
        continue
    if opt in ["-a"]:
        a0, a1 = arg.split(",")
        aparm = [int(a0), float(a1) * 1000]
        if aparm[1] < 0 or aparm[1] > 1000 or aparm[0] < 1:
            help()
        continue

if vparm == 0 or len(args) > 0:
    human = False

if logfile == "":
    if os.path.exists(dirname + "logs"):
        if not os.path.isdir(dirname + "logs"):
            help()
    else:
        try:
            os.mkdir(dirname + "logs")
        except WindowsError:
            help()
    logfile = dirname + "logs\\" + time.strftime("%Y%m%d-%H%M%S") + ".log"

try:
    output = open(logfile, "w")
except IOError:
    help()
output.write("=== " + program + " ===\n\n")
output.flush()


def log(s):
    if logfile != "":
        output.write(f"[{len(moves):03}] {s}\n")
        output.flush()


isBookDatExist(dirname)


def sm2str(s, size):
    if not s:
        return "PASS"
    return f"{'ABCDEFGHJKLMNOPQRST'['abcdefghijklmnopqrs'.find(s[0])]}{size - 'abcdefghijklmnopqrs'.find(s[1])}"


def variations(gt0, h0, c0, cc, size):
    global booksgf

    h1 = h0
    c1 = c0
    isover1 = False
    for n in gt0.nodes:
        if c1 in n.properties:
            m = sm2str(n.properties[c1][0], size)
            if "N" in n.properties:
                mw = "_".join([m] + n.properties["N"][0].split())
            else:
                mw = m
            if (
                c1 == cc
                and ("DO" not in n.properties)
                and (not ("BM" in n.properties and n.properties["BM"][0] in ["1", "2"]))
            ):
                if h1 in booksgf:
                    if not mw in booksgf[h1]:
                        booksgf[h1].append(mw)
                else:
                    booksgf[h1] = [mw]
            h1 = f"{h1} {m}"
            c1 = "B" if c1 == "W" else "W"
        else:
            if ("B" if c1 == "W" else "W") in n.properties:
                isover1 = True
                break
    if not isover1:
        for gt1 in gt0.children:
            variations(gt1, h1, c1, cc, size)


if os.path.exists(dirname + "book_19B.sgf"):
    try:
        sgffile = open(dirname + "book_19B.sgf", "r")
    except IOError:
        show("Failed to open the book file book_19B.sgf.")
        sys.exit()
    try:
        gt = sgf.parse(sgffile.read())[0]
    except sgf.ParseException:
        show("Failed to open the book file book_19B.sgf.")
        sys.exit()
    sgffile.close()

    h = "19"
    c = "B"
    isover = False
    for n in gt.nodes[1:]:
        if c in n.properties:
            m = sm2str(n.properties[c][0], 19)
            if "N" in n.properties:
                mw = "_".join([m] + n.properties["N"][0].split())
            else:
                mw = m
            if c == "B" and ("DO" not in n.properties):
                if h in booksgf:
                    if not mw in booksgf[h]:
                        booksgf[h].append(mw)
                else:
                    booksgf[h] = [mw]
            h = f"{h} {m}"
            c = "B" if c == "W" else "W"
        else:
            if ("B" if c == "W" else "W") in n.properties:
                isover = True
                break
    if not isover:
        for gt1 in gt.children:
            variations(gt1, h, c, "B", 19)

if os.path.exists(dirname + "book_19W.sgf"):
    try:
        sgffile = open(dirname + "book_19W.sgf", "r")
    except IOError:
        show("Failed to open the book file book_19W.sgf.")
        sys.exit()
    try:
        gt = sgf.parse(sgffile.read())[0]
    except sgf.ParseException:
        show("Failed to open the book file book_19W.sgf.")
        sys.exit()
    sgffile.close()

    h = "19"
    c = "B"
    isover = False
    for n in gt.nodes[1:]:
        if c in n.properties:
            m = sm2str(n.properties[c][0], 19)
            if "N" in n.properties:
                mw = "_".join([m] + n.properties["N"][0].split())
            else:
                mw = m
            if c == "W" and ("DO" not in n.properties):
                if h in booksgf:
                    if not mw in booksgf[h]:
                        booksgf[h].append(mw)
                else:
                    booksgf[h] = [mw]
            h = f"{h} {m}"
            c = "B" if c == "W" else "W"
        else:
            if ("B" if c == "W" else "W") in n.properties:
                isover = True
                break
    if not isover:
        for gt1 in gt.children:
            variations(gt1, h, c, "W", 19)


try:
    zen = CDLL(dirname + "Zen.dll")
except WindowsError:
    show("Zen.dll is missing.")
    sys.exit()
if vparm >= 2:
    if os.path.exists(dirname + "gnuplot\\gnuplot.exe"):
        gnuplot_exe = dirname + "gnuplot\\gnuplot.exe"
    else:
        gnuplot_exe = dirname + "gnuplot\\bin\\gnuplot.exe"
    try:
        gnuplot = subprocess.Popen(
            [gnuplot_exe],
            universal_newlines=True,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    except WindowsError:
        show("gnuplot.exe is missing.")
        sys.exit()
    if vparm == 2:
        gnuplot.stdin.write('set term wxt title "X: Count^0.5, Y: Value"\n')
    elif vparm == 3:
        gnuplot.stdin.write('set term wxt title "X: Move, Y: Value"\n')
    gnuplot.stdin.flush()


# zenClearBoard = zen[2]
zenGetNextColor = zen[7]
zenGetNumBlackPrisoners = zen[8]
zenGetNumWhitePrisoners = zen[9]
# zenGetPolicyKnowledge = zen[10]
# zenGetTopMoveInfo = zen[12]
# zenInitialize = zen[13]
zenIsLegal = zen[15]
zenIsThinking = zen[17]
# zenPass = zen[19]
# zenPlay = zen[20]
zenSetBoardSize = zen[22]
zenSetKomi = zen[23]
zenSetMaxTime = zen[24]
zenSetNumberOfSimulations = zen[26]
zenSetNumberOfThreads = zen[27]
zenSetPnLevel = zen[28]
zenSetPnWeight = zen[29]
zenSetVnMixRate = zen[30]
zenStartThinking = zen[31]
zenStopThinking = zen[32]
# zenUndo = zen[35]


def zenClearBoard():
    global moves, values, mainpv
    if len(moves) > 0:
        output.write("=== End ===\n\n")
        output.flush()
    moves = []
    values = []
    mainpv = []
    if vparm > 0:
        frame.SetTitle(program)
        listctrl.DeleteAllItems()
    zen[2]()


def zenGetPolicyKnowledge():
    k1 = ((c_int * 19) * 19)()
    zen[10](k1)
    while True:
        k2 = ((c_int * 19) * 19)()
        zen[10](k2)
        if sum([k1[y][x] == k2[y][x] for y in range(19) for x in range(19)]) == 361:
            break
        k1 = k2
    return k1


def zenGetTerritoryStatictics():
    t = ((c_int * 19) * 19)()
    zen[11](t)
    return t


topmoveinfo = []


def zenGetTopMoveInfo(n):
    global topmoveinfo

    if n == 0:
        topmoveinfo = []
        topmovexy = []
        topmovesump = 0
        for i in range(5):
            x, y, p, w, s = (
                c_int(0),
                c_int(0),
                c_int(0),
                c_float(0),
                create_string_buffer(100),
            )
            zen[12](i, byref(x), byref(y), byref(p), byref(w), s, 99)
            if p.value > 0 and [x.value, y.value] not in topmovexy:
                topmoveinfo.append(
                    [x.value, y.value, p.value, w.value, s.value.decode().rstrip(), 0]
                )
                topmovexy.append([x.value, y.value])
                topmovesump += p.value
        for item in topmoveinfo:
            item[5] = item[2] * 1.0 / topmovesump
    if n < len(topmoveinfo):
        return topmoveinfo[n]
    else:
        return [-1, -1, 0, 0, "", 0]


def zenCleanGunplot():
    while True:
        gnuplot.stdout.readline()


def zenCleanGunplot2():
    while True:
        gnuplot.stderr.readline()


def zenInitialize():
    if vparm >= 2:
        th = threading.Thread(target=zenCleanGunplot)
        th.setDaemon(True)
        th.start()
        th = threading.Thread(target=zenCleanGunplot2)
        th.setDaemon(True)
        th.start()
    zen[13]("")


def zenGetBookMove(moves1):
    mlist, mlistsgf = {}, {}
    for n in range(8):
        tmoves = [transform(m, n) for m in moves1]
        if len(moves1) <= 2:
            games = [(f"{boardsize} {' '.join(tmoves)}").strip()]
        elif len(moves1) == 3:
            tmoves3 = [
                [tmoves[0], tmoves[1], tmoves[2]],
                [tmoves[2], tmoves[1], tmoves[0]],
            ]
            games = [f"{boardsize} {' '.join(item)}" for item in tmoves3]
        elif len(moves1) == 4:
            tmoves4 = [
                [tmoves[0], tmoves[1], tmoves[2], tmoves[3]],
                [tmoves[0], tmoves[3], tmoves[2], tmoves[1]],
                [tmoves[2], tmoves[1], tmoves[0], tmoves[3]],
                [tmoves[2], tmoves[3], tmoves[0], tmoves[1]],
            ]
            games = [f"{boardsize} {' '.join(item)}" for item in tmoves4]
        elif len(moves1) == 5:
            tmoves5 = [
                [tmoves[0], tmoves[1], tmoves[2], tmoves[3], tmoves[4]],
                [tmoves[0], tmoves[3], tmoves[2], tmoves[1], tmoves[4]],
                [tmoves[0], tmoves[1], tmoves[4], tmoves[3], tmoves[2]],
                [tmoves[0], tmoves[3], tmoves[4], tmoves[1], tmoves[2]],
                [tmoves[4], tmoves[1], tmoves[2], tmoves[3], tmoves[0]],
                [tmoves[4], tmoves[3], tmoves[2], tmoves[1], tmoves[0]],
                [tmoves[2], tmoves[1], tmoves[0], tmoves[3], tmoves[4]],
                [tmoves[2], tmoves[3], tmoves[0], tmoves[1], tmoves[4]],
                [tmoves[4], tmoves[1], tmoves[0], tmoves[3], tmoves[2]],
                [tmoves[4], tmoves[3], tmoves[0], tmoves[1], tmoves[2]],
                [tmoves[2], tmoves[1], tmoves[4], tmoves[3], tmoves[0]],
                [tmoves[2], tmoves[3], tmoves[4], tmoves[1], tmoves[0]],
            ]
            games = [f"{boardsize} {' '.join(item)}" for item in tmoves5]
        else:
            tmoves6 = [
                [tmoves[0], tmoves[1], tmoves[2], tmoves[3], tmoves[4], tmoves[5]],
                [tmoves[0], tmoves[3], tmoves[2], tmoves[1], tmoves[4], tmoves[5]],
                [tmoves[0], tmoves[1], tmoves[2], tmoves[5], tmoves[4], tmoves[3]],
                [tmoves[0], tmoves[3], tmoves[2], tmoves[5], tmoves[4], tmoves[1]],
                [tmoves[0], tmoves[5], tmoves[2], tmoves[1], tmoves[4], tmoves[3]],
                [tmoves[0], tmoves[5], tmoves[2], tmoves[3], tmoves[4], tmoves[1]],
                [tmoves[0], tmoves[1], tmoves[4], tmoves[3], tmoves[2], tmoves[5]],
                [tmoves[0], tmoves[3], tmoves[4], tmoves[1], tmoves[2], tmoves[5]],
                [tmoves[0], tmoves[1], tmoves[4], tmoves[5], tmoves[2], tmoves[3]],
                [tmoves[0], tmoves[3], tmoves[4], tmoves[5], tmoves[2], tmoves[1]],
                [tmoves[0], tmoves[5], tmoves[4], tmoves[1], tmoves[2], tmoves[3]],
                [tmoves[0], tmoves[5], tmoves[4], tmoves[3], tmoves[2], tmoves[1]],
                [tmoves[2], tmoves[1], tmoves[0], tmoves[3], tmoves[4], tmoves[5]],
                [tmoves[2], tmoves[3], tmoves[0], tmoves[1], tmoves[4], tmoves[5]],
                [tmoves[2], tmoves[1], tmoves[0], tmoves[5], tmoves[4], tmoves[3]],
                [tmoves[2], tmoves[3], tmoves[0], tmoves[5], tmoves[4], tmoves[1]],
                [tmoves[2], tmoves[5], tmoves[0], tmoves[1], tmoves[4], tmoves[3]],
                [tmoves[2], tmoves[5], tmoves[0], tmoves[3], tmoves[4], tmoves[1]],
                [tmoves[2], tmoves[1], tmoves[4], tmoves[3], tmoves[0], tmoves[5]],
                [tmoves[2], tmoves[3], tmoves[4], tmoves[1], tmoves[0], tmoves[5]],
                [tmoves[2], tmoves[1], tmoves[4], tmoves[5], tmoves[0], tmoves[3]],
                [tmoves[2], tmoves[3], tmoves[4], tmoves[5], tmoves[0], tmoves[1]],
                [tmoves[2], tmoves[5], tmoves[4], tmoves[1], tmoves[0], tmoves[3]],
                [tmoves[2], tmoves[5], tmoves[4], tmoves[3], tmoves[0], tmoves[1]],
                [tmoves[4], tmoves[1], tmoves[0], tmoves[3], tmoves[2], tmoves[5]],
                [tmoves[4], tmoves[3], tmoves[0], tmoves[1], tmoves[2], tmoves[5]],
                [tmoves[4], tmoves[1], tmoves[0], tmoves[5], tmoves[2], tmoves[3]],
                [tmoves[4], tmoves[3], tmoves[0], tmoves[5], tmoves[2], tmoves[1]],
                [tmoves[4], tmoves[5], tmoves[0], tmoves[1], tmoves[2], tmoves[3]],
                [tmoves[4], tmoves[5], tmoves[0], tmoves[3], tmoves[2], tmoves[1]],
                [tmoves[4], tmoves[1], tmoves[2], tmoves[3], tmoves[0], tmoves[5]],
                [tmoves[4], tmoves[3], tmoves[2], tmoves[1], tmoves[0], tmoves[5]],
                [tmoves[4], tmoves[1], tmoves[2], tmoves[5], tmoves[0], tmoves[3]],
                [tmoves[4], tmoves[3], tmoves[2], tmoves[5], tmoves[0], tmoves[1]],
                [tmoves[4], tmoves[5], tmoves[2], tmoves[1], tmoves[0], tmoves[3]],
                [tmoves[4], tmoves[5], tmoves[2], tmoves[3], tmoves[0], tmoves[1]],
            ]
            games = [f"{boardsize} {' '.join(item + tmoves[6:])}" for item in tmoves6]
        for game in games:
            if game in booksgf:
                for m in booksgf[game]:
                    lm = m.split("_")
                    m = transform(lm[0], -n)
                    if m not in mlistsgf:
                        mlistsgf[m] = []
                    for w in lm[1:]:
                        if w not in mlistsgf[m]:
                            mlistsgf[m].append(w)
        for game in games:
            if game in book:
                for m in book[game]:
                    lm = m.split("_")
                    m = transform(lm[0], -n)
                    if m not in mlist:
                        mlist[m] = []
                    for w in lm[1:]:
                        if w not in mlist[m]:
                            mlist[m].append(w)
    return mlistsgf if mlistsgf else mlist


def zenPass(c):
    global mainpv
    moves.append("PASS")
    if len(mainpv) > 0 and mainpv[0] == "PASS":
        mainpv = mainpv[1:]
    else:
        mainpv = []
    zen[19](c)


def zenPlay(x, y, c):
    global mainpv
    m = xy2str(x, y)
    moves.append(m)
    if len(mainpv) > 0 and mainpv[0] == m:
        mainpv = mainpv[1:]
    else:
        mainpv = []
    zen[20](x, y, c)


# def zenSetBoardSize(n):
#    zen[22](n)

# def zenSetKomi(k1, k2):
#    zen[23](c_float(k1 + k2))


def zenUndo(n):
    global moves, values, mainpv
    moves = moves[:-n]
    values = values[:-n]
    mainpv = []
    zen[35](n)


def zenPlot(data):
    gnuplot.stdin.write(
        "plot "
        + ", ".join([(f'"-" title "{item[0]}"  with lines') for item in data])
        + "\n"
        + "".join(
            [
                "\n".join([(f"{xy[0]} {xy[1]}") for xy in item[1:]]) + "\ne\n"
                for item in data
            ]
        )
    )
    gnuplot.stdin.flush()


def lzPlot2():
    gnuplot.stdin.write(
        "plot "
        + '"-" title "" with linespoints\n'
        + "\n".join(
            [(f"{i + 1} {values[i]:.2f}") for i in range(len(moves)) if values[i] >= 0]
        )
        + "\ne\n"
    )
    gnuplot.stdin.flush()


def zenAntiMove(c, k):
    if vparm:
        frame.SetTitle(f"* Move {len(moves) + 1} ({program})")
        listctrl.DeleteAllItems()
        listctrl.InsertStringItem(0, "")
        points = [[], [], [], [], [], [], [], [], [], [], []]
        gfxcmd2 = "   gogui-gfx:\n"
        for y in range(boardsize):
            for x in range(boardsize):
                if k[y][x] >= aparm[1]:
                    gfxcmd2 += f"   LABEL {xy2str(x, y)} {k[y][x]}\n"
                points[max(0, k[y][x]) / 100].append(xy2str(x, y))
        gfxcmd2 += (
            "\n".join(
                [
                    f"   COLOR #{int(25.5 * (c - 1) * i + 12.8 * (10 - i)):02X}{int(25.5 * (2 - c) * i + 12.8 * (10 - i)):02X}{int(12.8 * (10 - i)):02X} {' '.join(points[i])}"
                    for i in range(1, 11)
                    if points[i]
                ]
            )
            + "\n "
        )
    dykomi = (
        komi[2] * (1 - len(moves) / komi[1])
        if boardsize == 19 and len(moves) < komi[1]
        else 0
    )
    zenSetKomi(c_float(komi[0] + dykomi * (2 * c - 3)))
    zenSetVnMixRate(
        c_float(weight[0] + (weight[1] - weight[0]) * min(1.0, len(moves) / 200.0))
    )
    xylist = [
        [x, y, k[y][x]]
        for y in range(boardsize)
        for x in range(boardsize)
        if k[y][x] >= aparm[1]
    ]
    xylist.sort(key=lambda item: -item[2])
    amlist = []
    wmax = 0.0
    pvA = [[""]]
    for xy in xylist:
        x, y = xy[0], xy[1]
        m = xy2str(x, y)
        zen[20](x, y, c)
        show("* play " + int2bw(c) + " " + m)
        zenStartThinking(3 - c)
        if vparm:
            #            show('')
            listctrl.InsertStringItem(0, int2bw(c) + " " + m)
            listctrl.SetStringItem(0, 4, f"{k[y][x] / 1000.0:.3f}")
            listctrl.SetStringItem(0, 5, m)
        #            selected = listctrl.GetFirstSelected()
        #            if selected >= 0: listctrl.Select(selected + 1)
        p0, w0, s0, e0 = 0, 0, "", 0
        while True:
            time.sleep(1.0)
            x1, y1, p1, w1, s1, e1 = zenGetTopMoveInfo(0)
            if p1 == 0:
                continue
            w1 = 1 - w1
            s1 = m + " " + s1
            if vparm:
                listctrl.SetStringItem(
                    0, 1, f"{p1} {'+' if p1 > p0 and p1 <= aparm[0] else '='}"
                )
                listctrl.SetStringItem(
                    0,
                    2,
                    f"{e1 * 100:.2f} {'=' if p1 > aparm[0] or e1 == e0 else '+' if e1 > e0 else '-'}",
                )
                listctrl.SetStringItem(
                    0,
                    3,
                    f"{w1 * 100:.2f} {'=' if p1 > aparm[0] or w1 == w0 else '+' if w1 > w0 else '-'}",
                )
                if s1 != s0:
                    listctrl.SetStringItem(0, 5, s1)
                selected = listctrl.GetFirstSelected()
                if selected > len(amlist):
                    sqB, pvB = [], []
                    if pvA:
                        show(gfxcmd2)
                else:
                    if selected <= 0:
                        sqB = s1.split()[:nparm]
                    else:
                        sqB = amlist[-selected][5].split()[:nparm]
                    pvB = [
                        f"{int2bw(2 - (c + i) % 2)} {sqB[i]}" for i in range(len(sqB))
                    ]
                    if pvB != pvA:
                        if nparm > 1:
                            show(
                                f"   gogui-gfx:\n   VAR {' '.join(pvB)}\n   COLOR {'#FF0000' if c == 2 else '#00FF00'} {sqB[0]}\n "
                            )
                        else:
                            show(f"   gogui-gfx: VAR {' '.join(pvB)}\n ")
                pvA = pvB
            p0, w0, s0, e0 = p1, w1, s1, e1
            if (
                p1 > aparm[0]
                or p1 ** (-0.5) + w1 * uparm < aparm[0] ** (-0.5) + wmax * uparm
            ):
                zenStopThinking()
                show("* undo\n")
                zen[35](1)
                amlist.append([x, y, p1, w1, k[y][x], s1, e1])
                if w1 > wmax:
                    wmax = w1
                break
    amlist.sort(key=lambda item: -item[3])
    if vparm:
        frame.SetTitle(f"Move {len(moves) + 1} ({program})")

    return amlist


stopThinking = False
stopThinking2 = False
isThinking = False
indexSelected = 0
sgfmove = ""
time0 = 0


def zenGenMove(c, k, a):
    dykomi = (
        komi[2] * (1 - len(moves) / komi[1])
        if boardsize == 19 and len(moves) < komi[1]
        else 0
    )
    zenSetKomi(c_float(komi[0] + dykomi * (2 * c - 3)))
    zenSetVnMixRate(
        c_float(weight[0] + (weight[1] - weight[0]) * min(1.0, len(moves) / 200.0))
    )
    zenStartThinking(c)

    global stopThinking2, isThinking, minput
    global mainpv
    minput = ""
    isThinking = True
    stopThinking2 = False

    topA = []
    pvA = []
    total5 = 0
    plotdata = []

    if vparm:
        if sgfmove:
            frame.SetTitle(f"* Move {len(moves) + 1} {sgfmove} ({program})")
        else:
            frame.SetTitle(f"* Move {len(moves) + 1} ({program})")
        listctrl.DeleteAllItems()
        listctrl.InsertStringItem(0, "")
        points = [[], [], [], [], [], [], [], [], [], [], []]
        gfxcmd2 = "   gogui-gfx:\n"
        for y in range(boardsize):
            for x in range(boardsize):
                if k[y][x] >= 100:
                    gfxcmd2 += f"   LABEL {xy2str(x, y)} {k[y][x]}\n"
                points[max(0, k[y][x]) / 100].append(xy2str(x, y))
        gfxcmd2 += (
            "\n".join(
                [
                    f"   COLOR #{int(25.5 * (c - 1) * i + 12.8 * (10 - i)):02X}{int(25.5 * (2 - c) * i + 12.8 * (10 - i)):02X}{int(12.8 * (10 - i)):02X} {' '.join(points[i])}"
                    for i in range(1, 11)
                    if points[i]
                ]
            )
            + "\n \n"
        )

    while zenIsThinking() != -0x80000000:
        time.sleep(1.0)

        topB, incB = [], []
        xylistA = [itemA[0:2] for itemA in topA]
        for n in range(5):
            x, y, p, w, s, e = zenGetTopMoveInfo(n)
            if p == 0:
                break
            #            w = max(0.0, min(1.0, w + dykomi/100.0))
            if [x, y] in xylistA:
                m = xylistA.index([x, y])
                topB.append(
                    [
                        x,
                        y,
                        p,
                        w,
                        s,
                        e,
                        "+" if p > topA[m][2] else "=",
                        "+" if w > topA[m][3] else "-" if w < topA[m][3] else "=",
                        "+" if e > topA[m][5] else "-" if e < topA[m][5] else "=",
                        0 if s.split()[0] == "pass" else k[y][x],
                    ]
                )
                incB.append(p - topA[m][2])
            else:
                topB.append(
                    [
                        x,
                        y,
                        p,
                        w,
                        s,
                        e,
                        "+",
                        "+",
                        "+",
                        0 if s.split()[0] == "pass" else k[y][x],
                    ]
                )
                incB.append(p)
        if incB and max(incB) > 0:
            topB[incB.index(max(incB))][6] = "#"
        if uparm > 0:
            topB.sort(key=lambda itemB: (itemB[2] ** (-0.5) - itemB[3] * uparm))

        xylistB = [itemB[0:2] for itemB in topB]
        sum5 = sum([itemB[2] for itemB in topB])
        for itemA in topA:
            if not itemA[0:2] in xylistB:
                topB.append(itemA[:])
                topB[-1][5] = itemA[2] * 1.0 / sum5
                topB[-1][6], topB[-1][7] = "=", "="
                topB[-1][8] = (
                    "+"
                    if topB[-1][5] > itemA[5]
                    else "-"
                    if topB[-1][5] < itemA[5]
                    else "="
                )

        if topB and topB != topA:
            if (
                a == 0
                and human
                and stopThinking2
                and (
                    len(topA) <= indexSelected
                    or topA[indexSelected][:2] != topB[indexSelected][:2]
                )
            ):
                stopThinking2 = False

            if vparm:
                for i in range(len(topA)):
                    itemA = topA[i]
                    itemB = topB[i]
                    if itemA != itemB:
                        if itemA[2] != itemB[2] or itemA[6] != itemB[6]:
                            listctrl.SetStringItem(i, 1, f"{itemB[2]} {itemB[6]}")
                        if (
                            f"{itemA[5] * 100:.2f} {itemA[8]}"
                            != f"{itemB[5] * 100:.2f} {itemB[8]}"
                        ):
                            listctrl.SetStringItem(
                                i, 2, f"{itemB[5] * 100:.2f} {itemB[8]}"
                            )
                        if (
                            f"{itemA[3] * 100:.2f} {itemA[7]}"
                            != f"{itemB[3] * 100:.2f} {itemB[7]}"
                        ):
                            listctrl.SetStringItem(
                                i, 3, f"{itemB[3] * 100:.2f} {itemB[7]}"
                            )
                        if itemA[4] != itemB[4]:
                            listctrl.SetStringItem(i, 5, itemB[4])
                            if itemA[4].split()[0] != itemB[4].split()[0]:
                                listctrl.SetStringItem(
                                    i, 0, int2bw(c) + " " + itemB[4].split()[0]
                                )
                                listctrl.SetStringItem(i, 4, f"{itemB[9] / 1000.0:.3f}")
                for i in range(len(topA), len(topB)):
                    itemB = topB[i]
                    listctrl.InsertStringItem(i, int2bw(c) + " " + itemB[4].split()[0])
                    listctrl.SetStringItem(i, 1, f"{itemB[2]} {itemB[6]}")
                    listctrl.SetStringItem(i, 2, f"{itemB[5] * 100:.2f} {itemB[8]}")
                    listctrl.SetStringItem(i, 3, f"{itemB[3] * 100:.2f} {itemB[7]}")
                    listctrl.SetStringItem(i, 4, f"{itemB[9] / 1000.0:.3f}")
                    listctrl.SetStringItem(i, 5, itemB[4])
                selected = listctrl.GetFirstSelected()
                if (
                    selected >= 0
                    and selected < len(topA)
                    and topA[selected][:2] != topB[selected][:2]
                ):
                    selected = [itemB[:2] for itemB in topB].index(topA[selected][:2])
                    listctrl.Select(selected)
                #                elif selected == len(topA) and selected < len(topB):
                #                    selected = len(topB)
                #                    listctrl.Select(selected)
                if selected < len(topB):
                    sqB = topB[max(0, selected)][4].split()[:nparm]
                    pvB = [
                        f"{int2bw(2 - (c + i) % 2)} {sqB[i]}" for i in range(len(sqB))
                    ]
                    if nparm > 1:
                        gfxcmd = (
                            (
                                f"   gogui-gfx:\n   VAR {' '.join(pvB)}\n   COLOR {'#FF0000' if c == 2 else '#00FF00'} {sqB[0]}\n \n"
                            )
                            if pvB != pvA
                            else ""
                        )
                    else:
                        gfxcmd = (
                            (f"   gogui-gfx: VAR {' '.join(pvB)}\n \n")
                            if pvB != pvA
                            else ""
                        )
                else:
                    sqB, pvB = [], []
                    gfxcmd = gfxcmd2 if pvA or not topA else ""

            show(
                " \n"
                + (gfxcmd if vparm and a == 0 and len(args) == 0 else "")
                + "\n".join(  # GTP Shell
                    [
                        f" {'!' if itemB[4].split()[0] == sgfmove else ' '} {int2bw(c)} {itemB[4].split()[0]:<4}-> {itemB[2]:>8} [{itemB[6]}], {itemB[5]:>6.2%} [{itemB[8]}], {itemB[3]:>6.2%} [{itemB[7]}], {itemB[9] / 1000.0:.3f}, {itemB[4]}"
                        for itemB in topB
                    ]
                )
            )

            if vparm == 2:
                total5B = sum([itemB[2] for itemB in topB][:5])
                for itemB in topB[:5]:
                    if itemB[6] == "=" or itemB[2] <= gparm[0]:
                        continue
                    m = itemB[4].split()[0]
                    if m in [i[0] for i in plotdata]:
                        n = [i[0] for i in plotdata].index(m)
                        plotdata[n].append([itemB[2] ** 0.5, itemB[3] * 100])
                    else:
                        plotdata.append([m, [itemB[2] ** 0.5, itemB[3] * 100]])
                if total5B > total5 + gparm[1] and plotdata:
                    zenPlot(plotdata)
                    total5 = total5B
            topA = topB
            if vparm:
                pvA = pvB

        if topA:
            psubmax = max([itemA[2] for itemA in topA[1:]] + [0])
            if (
                (
                    a == 0
                    and (not human)
                    and (
                        (
                            len(moves) >= strength[0]
                            and topA[0][2] > min(strength[1], psubmax + strength[2])
                        )
                        or (topA[0][2] > Qparm[0] and topA[0][5] > Qparm[1])
                        or time.time() - time0 + 1.0 > maxtime
                        or topA[0][2] > min(Strength[0], psubmax + Strength[1])
                    )
                )
                or (a == 0 and human and stopThinking2 and selected < len(topA))
                or (a == 1 and stopThinking)
            ):
                break
    if vparm:
        if minput:
            frame.SetTitle(f"Move {len(moves) + 1} {minput} ({program})")
        elif sgfmove:
            frame.SetTitle(f"Move {len(moves) + 1} {sgfmove} ({program})")
        else:
            frame.SetTitle(f"Move {len(moves) + 1} ({program})")
        if topA == []:
            listctrl.InsertStringItem(0, int2bw(c) + " " + "pass")
            #            listctrl.SetStringItem(0, 1, '? ?')
            #            listctrl.SetStringItem(0, 2, '? ?')
            listctrl.SetStringItem(0, 4, "0.000")
            listctrl.SetStringItem(0, 5, "pass")

    show(" ")
    if zenIsThinking() != -0x80000000:
        show(
            f"   Komi:       {komi[0]:.1f} {'+' if dykomi * (2 * c - 3) >= 0 else '-'} {abs(dykomi):.1f}"
        )
        zenStopThinking()
        show(" ")

    isThinking = False
    return topA


def zenSetPriority(p):
    priorities = [
        win32process.IDLE_PRIORITY_CLASS,
        win32process.BELOW_NORMAL_PRIORITY_CLASS,
        win32process.NORMAL_PRIORITY_CLASS,
        win32process.ABOVE_NORMAL_PRIORITY_CLASS,
        win32process.HIGH_PRIORITY_CLASS,
    ]
    win32process.SetPriorityClass(
        win32api.OpenProcess(
            win32con.PROCESS_ALL_ACCESS, True, win32api.GetCurrentProcessId()
        ),
        priorities[p],
    )
    if vparm == 2:
        win32process.SetPriorityClass(
            win32api.OpenProcess(win32con.PROCESS_ALL_ACCESS, True, gnuplot.pid),
            priorities[p],
        )


def zenStopThinking2(event):
    global stopThinking2, indexSelected
    stopThinking2 = True
    indexSelected = max(0, listctrl.GetFirstSelected())


minput = ""


def zenOnKeyPress(event):
    global minput

    if isThinking == False or human == False:
        return

    keycode = event.GetKeyCode()
    if 65 <= keycode <= 84 and keycode != 73 and len(minput) == 0:
        minput += "ABCDEFGHIJKLMNOPQRST"[keycode - 65]
    elif 49 <= keycode <= 57 and len(minput) == 1:
        minput += "0123456789"[keycode - 48]
    elif 48 <= keycode <= 57 and len(minput) == 2 and minput[1] == "1":
        minput += "0123456789"[keycode - 48]
    elif keycode == 8:
        minput = minput[:-1]
    else:
        return
    if minput:
        frame.SetTitle(f"* Move {len(moves) + 1} {minput} ({program})")
    else:
        frame.SetTitle(f"* Move {len(moves) + 1} ({program})")


zenInitialize()
zenSetBoardSize(boardsize)
zenSetNumberOfThreads(threads)
zenSetNumberOfSimulations(1000000000)
zenSetMaxTime(c_float(1000000000.0))
zenSetPnLevel(fparm[0])
zenSetPnWeight(c_float(fparm[1]))
zenSetPriority(pparm)


class App(wx.App):
    def __init__(self):
        wx.App.__init__(self, redirect=False)

    def OnExit(self):
        if vparm == 2:
            gnuplot.stdin.write("quit\n")
            gnuplot.stdin.flush()


app = App()
frame = wx.Frame(
    None,
    title=program,
    size=(600 * 15 / 11, 300 * 15 / 11),
    style=wx.MINIMIZE_BOX
    | wx.CAPTION
    | wx.SYSTEM_MENU
    | wx.STAY_ON_TOP
    | wx.RESIZE_BORDER,
)
listctrl = wx.ListCtrl(frame, style=wx.LC_REPORT | wx.LC_SINGLE_SEL | wx.LC_HRULES)
listctrl.SetFont(
    wx.Font(
        15, family=wx.DEFAULT, style=wx.NORMAL, weight=wx.NORMAL, faceName="Consolas"
    )
)
listctrl.InsertColumn(0, "Move", wx.LIST_FORMAT_RIGHT, width=60 * 15 / 11)
listctrl.InsertColumn(1, "Count  ", wx.LIST_FORMAT_RIGHT, width=85 * 15 / 11)
listctrl.InsertColumn(2, "Effort  ", wx.LIST_FORMAT_RIGHT, width=85 * 15 / 11)
listctrl.InsertColumn(3, "Value  ", wx.LIST_FORMAT_RIGHT, width=85 * 15 / 11)
listctrl.InsertColumn(4, "Policy", wx.LIST_FORMAT_RIGHT, width=70 * 15 / 11)
listctrl.InsertColumn(5, "Sequence", width=350 * 15 / 11)
listctrl.Bind(wx.EVT_RIGHT_DOWN, zenStopThinking2)
listctrl.Bind(wx.EVT_RIGHT_DCLICK, zenStopThinking2)
listctrl.Bind(wx.EVT_KEY_DOWN, zenOnKeyPress)
if vparm:
    frame.Show()
    hWndList = []
    win32gui.EnumWindows(lambda hWnd, param: param.append(hWnd), hWndList)
    pid = win32api.GetCurrentProcessId()
    hWndList2 = [
        h
        for h in hWndList
        if win32gui.GetWindowText(h) == program
        and win32process.GetWindowThreadProcessId(h)[1] == pid
    ]
    if hWndList2:
        win32gui.ShowWindow(hWndList2[0], 1)

zenClearBoard()

sgfmoves = []


def variations2(gt0, c0):
    global sgfmoves

    c1 = c0
    isover1 = False
    for n in gt0.nodes:
        if c1 in n.properties:
            sgfmoves.append(sm2str(n.properties[c1][0], boardsize))
            c1 = "B" if c1 == "W" else "W"
        else:
            if ("B" if c1 == "W" else "W") in n.properties:
                isover1 = True
                break
    if not isover1 and len(gt0.children) > 0:
        variations2(gt0.children[0], c1)


def analysis_mode():
    global time0, sgfmove, boardsize, komi, values

    try:
        sgffile = open(args[1], "r")
    except IOError:
        show(f"Failed to open the sgf file {args[1]}.")
        sys.exit()
    try:
        gt = sgf.parse(sgffile.read())[0]
    except sgf.ParseException:
        show(f"Failed to open the sgf file {args[1]}.")
        sys.exit()
    sgffile.close()
    if len(gt.nodes) < 1:
        sys.exit()
    if "SZ" in gt.nodes[0].properties:
        boardsize = int(gt.nodes[0].properties["SZ"][0])
        zenSetBoardSize(boardsize)
    if "KM" in gt.nodes[0].properties:
        komi[0] = float(gt.nodes[0].properties["KM"][0])

    c = "B"
    isover = False
    for n in gt.nodes[1:]:
        if c in n.properties:
            sgfmoves.append(sm2str(n.properties[c][0], boardsize))
            c = "B" if c == "W" else "W"
        else:
            if ("B" if c == "W" else "W") in n.properties:
                isover = True
                break
    if not isover and len(gt.children) > 0:
        variations2(gt.children[0], c)

    sgfheader = f"(;CA[gb2312]SZ[{boardsize}]KM[{komi[0]:.1f}]GC[{program}]"
    sgfmod = ""
    sgfmod1 = ")"

    for i in range(len(sgfmoves)):
        time0 = time.time()
        c = zenGetNextColor()
        sm = sgfmoves[i]

        if ["analyze_black", "analyze_white"][i % 2] != args[0] or i < (Aparm[0] - 1):
            values.append(-1)
            if sm == "PASS":
                zenPass(c)
                log(int2bw(c) + " pass;")
                sgfmod += ";" + int2bw(c) + "[]"
            else:
                x, y = str2xy(sm)
                zenPlay(x, y, c)
                log(int2bw(c) + " " + sm + ";")
                sgfmod += (
                    ";"
                    + int2bw(c)
                    + "["
                    + "abcdefghijklmnopqrstuvwxyz"[x]
                    + "abcdefghijklmnopqrstuvwxyz"[y]
                    + "]"
                )
            continue

        if len(moves) < bparm[0]:
            mlist = zenGetBookMove(moves)
            mlist0 = list(mlist)
            mlist00 = ["_".join([m] + mlist[m]) for m in mlist0]
            if mlist:
                show(
                    (str(boardsize) + " " + " ".join(moves)).strip()
                    + " | "
                    + " ".join(mlist00)
                )
                show(" ")
                if sm == "PASS":
                    zenPass(c)
                    log(
                        int2bw(c)
                        + " pass"
                        + ("" if sm in mlist0 else " ...")
                        + "\n\n"
                        + (str(boardsize) + " " + " ".join(moves[:-1])).strip()
                        + " | "
                        + " ".join(mlist00)
                        + ";\n"
                    )
                    if sm in mlist0:
                        values.append(float(mlist[sm][0]) if mlist[sm] else -1)
                        if mlist[sm]:
                            sgfmod += (
                                ";"
                                + int2bw(c)
                                + f"[]N[book {float(mlist[sm][0]):.1f}]C[{float(mlist[sm][0]):.1f}]"
                            )
                        else:
                            sgfmod += ";" + int2bw(c) + "[]N[book]"
                    else:
                        m = random.choice(mlist0)
                        values.append(float(mlist[m][0]) if mlist[m] else -1)
                        sgfmod += "\n(;" + int2bw(c) + "[]DO[]"
                        x, y = str2xy(m)
                        if mlist[m]:
                            sgfmod2 = f"\n(;{int2bw(c)}[{'abcdefghijklmnopqrstuvwxyz'[x]}{'abcdefghijklmnopqrstuvwxyz'[y]}]N[book {float(mlist[m][0]):.1f}]C[{float(mlist[m][0]):.1f}]"
                        else:
                            sgfmod2 = f"\n(;{int2bw(c)}[{'abcdefghijklmnopqrstuvwxyz'[x]}{'abcdefghijklmnopqrstuvwxyz'[y]}]N[book]"
                        c1 = 3 - c
                        moves1 = moves[:-1] + [m]
                        while True:
                            mlist1 = zenGetBookMove(moves1)
                            if mlist1 == {}:
                                break
                            mlist10 = list(mlist1)
                            m1 = random.choice(mlist10)
                            x, y = str2xy(m1)
                            if mlist1[m1]:
                                sgfmod2 += f";{int2bw(c1)}[{'abcdefghijklmnopqrstuvwxyz'[x]}{'abcdefghijklmnopqrstuvwxyz'[y]}]N[book {float(mlist1[m1][0]):.1f}]C[{float(mlist1[m1][0]):.1f}]"
                            else:
                                sgfmod2 += f";{int2bw(c1)}[{'abcdefghijklmnopqrstuvwxyz'[x]}{'abcdefghijklmnopqrstuvwxyz'[y]}]N[book]"
                            c1 = 3 - c1
                            moves1.append(m1)
                        sgfmod2 += ")"
                        sgfmod1 = ")" + sgfmod2 + sgfmod1
                else:
                    x, y = str2xy(sm)
                    zenPlay(x, y, c)
                    log(
                        int2bw(c)
                        + " "
                        + sm
                        + ("" if sm in mlist0 else " ...")
                        + "\n\n"
                        + (str(boardsize) + " " + " ".join(moves[:-1])).strip()
                        + " | "
                        + " ".join(mlist00)
                        + ";\n"
                    )
                    if sm in mlist0:
                        values.append(float(mlist[sm][0]) if mlist[sm] else -1)
                        if mlist[sm]:
                            sgfmod += (
                                ";"
                                + int2bw(c)
                                + "["
                                + "abcdefghijklmnopqrstuvwxyz"[x]
                                + "abcdefghijklmnopqrstuvwxyz"[y]
                                + f"]N[book {float(mlist[sm][0]):.1f}]C[{float(mlist[sm][0]):.1f}]"
                            )
                        else:
                            sgfmod += (
                                ";"
                                + int2bw(c)
                                + "["
                                + "abcdefghijklmnopqrstuvwxyz"[x]
                                + "abcdefghijklmnopqrstuvwxyz"[y]
                                + "]N[book]"
                            )
                    else:
                        m = random.choice(mlist0)
                        values.append(float(mlist[m][0]) if mlist[m] else -1)
                        sgfmod += (
                            "\n(;"
                            + int2bw(c)
                            + "["
                            + "abcdefghijklmnopqrstuvwxyz"[x]
                            + "abcdefghijklmnopqrstuvwxyz"[y]
                            + "]DO[]"
                        )
                        x, y = str2xy(m)
                        if mlist[m]:
                            sgfmod2 = f"\n(;{int2bw(c)}[{'abcdefghijklmnopqrstuvwxyz'[x]}{'abcdefghijklmnopqrstuvwxyz'[y]}]N[book {float(mlist[m][0]):.1f}]C[{float(mlist[m][0]):.1f}]"
                        else:
                            sgfmod2 = f"\n(;{int2bw(c)}[{'abcdefghijklmnopqrstuvwxyz'[x]}{'abcdefghijklmnopqrstuvwxyz'[y]}]N[book]"
                        c1 = 3 - c
                        moves1 = moves[:-1] + [m]
                        while True:
                            mlist1 = zenGetBookMove(moves1)
                            if mlist1 == {}:
                                break
                            mlist10 = list(mlist1)
                            m1 = random.choice(mlist10)
                            x, y = str2xy(m1)
                            if mlist1[m1]:
                                sgfmod2 += f";{int2bw(c1)}[{'abcdefghijklmnopqrstuvwxyz'[x]}{'abcdefghijklmnopqrstuvwxyz'[y]}]N[book {float(mlist1[m1][0]):.1f}]C[{float(mlist1[m1][0]):.1f}]"
                            else:
                                sgfmod2 += f";{int2bw(c1)}[{'abcdefghijklmnopqrstuvwxyz'[x]}{'abcdefghijklmnopqrstuvwxyz'[y]}]N[book]"
                            c1 = 3 - c1
                            moves1.append(m1)
                        sgfmod2 += ")"
                        sgfmod1 = ")" + sgfmod2 + sgfmod1
                continue

        if (
            len(moves) < rparm[0]
            or [1 for i in range(len(moves)) if i % 2 == 1 and moves[i] != "PASS"] == []
        ):
            values.append(-1)
            if sm == "PASS":
                zenPass(c)
                log(int2bw(c) + " pass;")
                sgfmod += ";" + int2bw(c) + "[]"
            else:
                x, y = str2xy(sm)
                zenPlay(x, y, c)
                log(int2bw(c) + " " + sm + ";")
                sgfmod += (
                    ";"
                    + int2bw(c)
                    + "["
                    + "abcdefghijklmnopqrstuvwxyz"[x]
                    + "abcdefghijklmnopqrstuvwxyz"[y]
                    + "]"
                )
            continue

        if aparm[0] > 0:
            amlist = zenAntiMove(c, zenGetPolicyKnowledge())
            s = "\n".join(
                [
                    f"{int2bw(c)} {item[5].split()[0]:<4}-> {item[2]:>8}, {item[6]:>6.2%}, {item[3]:>6.2%}, {item[4] / 1000.0:.3f}, {item[5]}"
                    for item in amlist
                ]
            )
            if sm == "PASS":
                zenPass(c)
                if amlist[0][5].split()[0] == "pass":
                    log(int2bw(c) + " pass" + "\n\n" + s + ";\n")
                else:
                    log(f"{int2bw(c)} pass ({amlist[0][5].split()[0]})\n\n{s};\n")
            else:
                x, y = str2xy(sm)
                zenPlay(x, y, c)
                if amlist[0][5].split()[0] == sm:
                    log(int2bw(c) + " " + sm + "\n\n" + s + ";\n")
                else:
                    log(f"{int2bw(c)} {sm} ({amlist[0][5].split()[0]})\n\n{s};\n")
            continue

        if len(moves) > 0 and len(moves) % Aparm[2] == 0:
            valueall = "C["
            for i in range(len(moves)):
                if values[i] < 0:
                    continue
                valueall += f"{i + 1}, {values[i]:.1f}\n"
            valueall += "]"
            try:
                sgfout = open(args[2], "w")
            except IOError:
                show(f"Failed to open the sgf file {args[2]}.")
                sys.exit()
            sgfout.write(sgfheader + valueall + sgfmod + sgfmod1)
            sgfout.close()

        sgfmove = sm if sm != "PASS" else "pass"
        top = zenGenMove(c, zenGetPolicyKnowledge(), 0)
        sgfmove = ""
        if not top:
            values.append(-1)
            if sm == "PASS":
                lzPass(c)
                log(int2bw(c) + " pass;")
                sgfmod += ";" + int2bw(c) + "[]"
            else:
                x, y = str2xy(sm)
                lzPlay(x, y, c)
                log(int2bw(c) + " " + sm + ";")
                sgfmod += (
                    ";"
                    + int2bw(c)
                    + "["
                    + "abcdefghijklmnopqrstuvwxyz"[x]
                    + "abcdefghijklmnopqrstuvwxyz"[y]
                    + "]"
                )
            continue
        s = "\n".join(
            [
                f"{int2bw(c)} {item[4].split()[0]:<4}-> {item[2]:>8}, {item[5]:>6.2%}, {item[3]:>6.2%}, {item[9] / 1000.0:.3f}, {item[4]}"
                for item in top
            ]
        )
        values.append(top[0][3] * 100 if c == 2 else 100 - top[0][3] * 100)
        if sm == "PASS":
            zenPass(c)
            if top[0][4].split()[0] == "pass":
                log(int2bw(c) + " pass" + "\n\n" + s + ";\n")
                sgfmod += (
                    ";"
                    + int2bw(c)
                    + f"[]N[{top[0][3] * 100 if c == 2 else (100 - top[0][3] * 100):.1f}]C[{top[0][3] * 100 if c == 2 else (100 - top[0][3] * 100):.1f}]"
                )
            else:
                log(f"{int2bw(c)} pass ({top[0][4].split()[0]})\n\n{s};\n")
                sgfmod += "\n(;" + int2bw(c) + "[]DO[]"
                sgfmod2 = "\n("
                pv = top[0][4].split()[:nparm]
                for i in range(len(pv)):
                    if pv[i] == "pass":
                        sgfmod2 += f";{int2bw(2 - (c + i) % 2)}[]"
                    else:
                        x, y = str2xy(pv[i])
                        sgfmod2 += f";{int2bw(2 - (c + i) % 2)}[{'abcdefghijklmnopqrstuvwxyz'[x]}{'abcdefghijklmnopqrstuvwxyz'[y]}]"
                    if i == 0:
                        sgfmod2 += f"N[{top[0][3] * 100.0:.1f}]"
                sgfmod2 += ")"
                sgfmod1 = ")" + sgfmod2 + sgfmod1
        else:
            x, y = str2xy(sm)
            zenPlay(x, y, c)
            if top[0][4].split()[0] == sm:
                log(int2bw(c) + " " + sm + "\n\n" + s + ";\n")
                sgfmod += (
                    ";"
                    + int2bw(c)
                    + "["
                    + "abcdefghijklmnopqrstuvwxyz"[x]
                    + "abcdefghijklmnopqrstuvwxyz"[y]
                    + f"]N[{top[0][3] * 100.0 if c == 2 else (100 - top[0][3] * 100.0):.1f}]C[{top[0][3] * 100.0 if c == 2 else (100 - top[0][3] * 100.0):.1f}]"
                )
            else:
                log(f"{int2bw(c)} {sm} ({top[0][4].split()[0]})\n\n{s};\n")
                sgfmod += (
                    "\n(;"
                    + int2bw(c)
                    + "["
                    + "abcdefghijklmnopqrstuvwxyz"[x]
                    + "abcdefghijklmnopqrstuvwxyz"[y]
                    + "]DO[]"
                )
                sgfmod2 = "\n("
                pv = top[0][4].split()[:nparm]
                for i in range(len(pv)):
                    if pv[i] == "pass":
                        sgfmod2 += f";{int2bw(2 - (c + i) % 2)}[]"
                    else:
                        x, y = str2xy(pv[i])
                        sgfmod2 += f";{int2bw(2 - (c + i) % 2)}[{'abcdefghijklmnopqrstuvwxyz'[x]}{'abcdefghijklmnopqrstuvwxyz'[y]}]"
                    if i == 0:
                        sgfmod2 += f"N[{top[0][3] * 100.0:.1f}]"
                sgfmod2 += ")"
                sgfmod1 = ")" + sgfmod2 + sgfmod1
        if vparm == 3:
            lzPlot2()
        if len(moves) >= xparm[0] and (
            top[0][3] < xparm[1] or top[0][3] > (1 - xparm[1])
        ):
            break

    valueall = "C["
    for i in range(len(moves)):
        if values[i] < 0:
            continue
        valueall += f"{i + 1}, {values[i]:.1f}\n"
    valueall += "]"
    try:
        sgfout = open(args[2], "w")
    except IOError:
        show(f"Failed to open the sgf file {args[2]}.")
        sys.exit()
    sgfout.write(sgfheader + valueall + sgfmod + sgfmod1)
    sgfout.close()
    output.close()
    if vparm == 3:
        input("Press Enter to exit. ")
    wx.Exit()


afterbook = 0


def gtp_mode():
    global time0, stopThinking, boardsize, komi, mainpv
    global afterbook, values

    while True:
        cmd = input("").lower().split()
        time0 = time.time()
        stopThinking = True
        while isThinking:
            time.sleep(0.1)
        stopThinking = False

        if cmd == ["list_commands"]:
            reply(
                "\n".join(
                    [
                        "list_commands",
                        "name",
                        "version",
                        "protocol_version",
                        "quit",
                        "clear_board",
                        "boardsize",
                        "komi",
                        "undo",
                        "gg-undo",
                        "pass",
                        "play",
                        "genmove",
                        "genbook",
                        "gogui-analyze_commands",
                    ]
                )
            )
            continue

        if cmd == ["name"]:
            reply(name)
            continue

        if cmd == ["version"]:
            reply(version)
            continue

        if cmd == ["protocol_version"]:
            reply("2")
            continue

        if cmd == ["quit"]:
            reply("")
            break

        if cmd == ["clear_board"]:
            reply("")
            zenClearBoard()
            afterbook = 0
            continue

        if cmd[:-1] == ["boardsize"] and cmd[-1].isdigit() and 0 < int(cmd[-1]) <= 19:
            reply("")
            boardsize = int(cmd[-1])
            zenSetBoardSize(boardsize)
            continue

        if cmd[:-1] == ["komi"]:
            reply("")
            komi[0] = float(cmd[-1])
            continue

        if cmd == ["undo"] and len(moves) > 0:
            reply("")
            zenUndo(1)
            continue

        if cmd[:-1] == ["gg-undo"] and cmd[-1].isdigit() and len(moves) >= int(cmd[-1]):
            reply("")
            zenUndo(int(cmd[-1]))
            #            afterbook = max(afterbook - 1, 0)
            continue

        if cmd in [["play", "w", "pass"], ["play", "b", "pass"]]:
            reply("")
            c = zenGetNextColor()
            if [c, cmd[1]] in [[1, "b"], [2, "w"]]:
                m = "" if mainpv == [] else mainpv[0]
                values.append(-1)
                zenPass(c)
                log(int2bw(c) + f" pass{(f' ({m})') if m and m != 'pass' else ''};")
                c = 3 - c
            m = "" if mainpv == [] else mainpv[0]
            values.append(-1)
            zenPass(c)
            log(int2bw(c) + f" pass{(f' ({m})') if m and m != 'pass' else ''};")
            continue

        if (
            cmd[:-1] in [["play", "w"], ["play", "b"]]
            and len(cmd[-1]) >= 2
            and cmd[-1][0] in "abcdefghjklmnopqrstuvwxyz"[0:boardsize]
            and cmd[-1][1:].isdigit()
            and int(cmd[-1][1:]) in range(1, boardsize + 1)
        ):
            reply("")
            x, y = str2xy(cmd[-1])
            c = zenGetNextColor()
            if [c, cmd[1]] in [[1, "b"], [2, "w"]]:
                m = "" if mainpv == [] else mainpv[0]
                values.append(-1)
                zenPass(c)
                log(int2bw(c) + f" pass{(f' ({m})') if m and m != 'pass' else ''};")
                c = 3 - c
            m = "" if mainpv == [] else mainpv[0]
            values.append(-1)
            zenPlay(x, y, c)
            log(
                int2bw(c)
                + " "
                + cmd[-1].upper()
                + f"{(f' ({m})') if m and m != cmd[-1].upper() else ''};"
            )
            continue

        if cmd == ["genmove", "white"]:
            cmd = ["genmove", "w"]
        if cmd == ["genmove", "black"]:
            cmd = ["genmove", "b"]
        if cmd in [["genmove", "w"], ["genmove", "b"]]:
            c = zenGetNextColor()
            if [c, cmd[1]] in [[1, "b"], [2, "w"]]:
                m = "" if mainpv == [] else mainpv[0]
                values.append(-1)
                zenPass(c)
                log(int2bw(c) + f" pass{(f' ({m})') if m and m != 'pass' else ''};")
                c = 3 - c
            if len(moves) < bparm[0]:
                mlist = zenGetBookMove(moves)
                mlist0 = list(mlist)
                mlist00 = ["_".join([m] + mlist[m]) for m in mlist0]
                if mlist:
                    afterbook = 0
                    show(
                        (str(boardsize) + " " + " ".join(moves)).strip()
                        + " | "
                        + " ".join(mlist00)
                    )
                    show(" ")
                    m1 = random.choice(mlist0)
                    x, y = str2xy(m1)
                    zenPlay(x, y, c)
                    values.append(float(mlist[m1][0]) if mlist[m1] else -1)
                    log(
                        int2bw(c)
                        + " "
                        + m1
                        + "\n\n"
                        + (str(boardsize) + " " + " ".join(moves[:-1])).strip()
                        + " | "
                        + " ".join(mlist00)
                        + ";\n"
                    )
                    reply(m1)
                    continue
            afterbook += 1
            if afterbook > Xparm:
                reply("resign")
                log(int2bw(c) + " resign;")
                continue
            k = zenGetPolicyKnowledge()
            if (
                len(moves) < rparm[0]
                or [1 for i in range(len(moves)) if i % 2 == 1 and moves[i] != "PASS"]
                == []
            ):
                xx, yy = random.choice(
                    [
                        [x, y]
                        for y in range(boardsize)
                        for x in range(boardsize)
                        if k[y][x] >= rparm[1]
                    ]
                )
                m1 = xy2str(xx, yy)
                values.append(-1)
                zenPlay(xx, yy, c)
                log(int2bw(c) + " " + m1 + ";")
                reply(m1)
                continue
            xylist = [
                [x, y]
                for y in range(boardsize)
                for x in range(boardsize)
                if k[y][x] >= qparm[1]
            ]
            if len(xylist) == 1:
                mq = xy2str(xylist[0][0], xylist[0][1])
                if (len(mainpv) == 0 and len(moves) < qparm[0]) or (
                    len(mainpv) > 0 and mainpv[0] == mq
                ):
                    values.append(-1)
                    zenPlay(xylist[0][0], xylist[0][1], c)
                    log(int2bw(c) + " " + mq + ";")
                    reply(mq)
                    continue

            if aparm[0] > 0:
                amlist = zenAntiMove(c, k)
                s = "\n".join(
                    [
                        f"{int2bw(c)} {item[5].split()[0]:<4}-> {item[2]:>8}, {item[6]:>6.2%}, {item[3]:>6.2%}, {item[4] / 1000.0:.3f}, {item[5]}"
                        for item in amlist
                    ]
                )
                x, y = amlist[0][0], amlist[0][1]
                mainpv = amlist[0][5].split()
                m = xy2str(x, y)
                zenPlay(x, y, c)
                log(int2bw(c) + " " + m + "\n\n" + s + ";\n")
                reply(m)
                continue

            ispass, top = True, zenGenMove(c, k, 0)
            if top:
                s = "\n".join(
                    [
                        f"{int2bw(c)} {item[4].split()[0]:<4}-> {item[2]:>8}, {item[5]:>6.2%}, {item[3]:>6.2%}, {item[9] / 1000.0:.3f}, {item[4]}"
                        for item in top
                    ]
                )
                values.append(top[0][3] * 100 if c == 2 else (100 - top[0][3] * 100))
                if top[0][4].split()[0].lower() != "pass":
                    ispass = False
            if ispass == True:
                reply("pass")
                zenPass(c)
                log(int2bw(c) + " pass;")
                continue
            if top == [] or (top[0][3] < xparm[1] and len(moves) >= xparm[0]):
                reply("resign")
                log(int2bw(c) + " resign;")
                continue
            if (
                len(minput) > 1
                and minput[0] in "ABCDEFGHJKLMNOPQRSTUVWXYZ"
                and minput[1:].isdigit()
            ):
                if minput in [item[4].split()[0] for item in top]:
                    mainpv = top[[item[4].split()[0] for item in top].index(minput)][
                        4
                    ].split()
                else:
                    mainpv = [minput]
            else:
                mainpv = top[indexSelected if human else 0][4].split()
            m = mainpv[0]
            x, y = str2xy(m)
            if zenIsLegal(x, y, c) % 256 == 0:
                mainpv = top[indexSelected if human else 0][4].split()
                m = mainpv[0]
                x, y = str2xy(m)
            zenPlay(x, y, c)
            if vparm == 3:
                lzPlot2()
            if len(moves) <= bparm[0] and not human:
                booksgf[(str(boardsize) + " " + " ".join(moves[:-1])).strip()] = [
                    top[0][4].split()[0].upper()
                ] + [
                    item[4].split()[0].upper() for item in top[1:] if item[2] > bparm[1]
                ]
            log(
                int2bw(c)
                + " "
                + m
                + (f" ({top[0][4].split()[0]})" if top[0][4].split()[0] != m else "")
                + "\n\n"
                + s
                + ";\n"
            )
            reply(m)
            continue

        if cmd in [["genbook"], ["genbook", "w"], ["genbook", "b"]] and moves:
            cc = [0, 1] if len(cmd) == 1 else [1] if cmd[1] == "w" else [0]
            l = [
                (str(boardsize) + " " + " ".join(moves[:i])).strip() + " | " + moves[i]
                for i in range(len(moves))
                if i % 2 in cc and moves[i] != "PASS"
            ]
            reply("\n" + "\n".join(l) if l else "")
            continue

        if cmd == ["gogui-analyze_commands"]:
            reply(
                "\n".join(
                    [
                        "gfx/Policy Knowledge/policy_knowledge",
                        "gfx/Territory Statictics/territory_statictics",
                        "gfx/Analysis for Black/analyze_black",
                        "gfx/Analysis for White/analyze_white",
                    ]
                )
            )
            continue

        if cmd == ["policy_knowledge"]:
            c, k = zenGetNextColor(), zenGetPolicyKnowledge()
            points = [[], [], [], [], [], [], [], [], [], [], []]
            s = ""
            for y in range(boardsize):
                for x in range(boardsize):
                    if k[y][x] >= 100:
                        s += f"LABEL {xy2str(x, y)} {k[y][x]}\n"
                    points[max(0, k[y][x]) / 100].append(xy2str(x, y))
            reply(
                "\n"
                + s
                + "\n".join(
                    [
                        f"COLOR #{int(25.5 * (c - 1) * i + 12.8 * (10 - i)):02X}{int(25.5 * (2 - c) * i + 12.8 * (10 - i)):02X}{int(12.8 * (10 - i)):02X} {' '.join(points[i])}"
                        for i in range(1, 11)
                        if points[i]
                    ]
                )
            )
            continue

        if cmd == ["territory_statictics"]:
            t = zenGetTerritoryStatictics()
            pointsW, pointsB, pointsM = (
                [[], [], [], [], [], [], [], [], [], []],
                [[], [], [], [], [], [], [], [], [], []],
                [],
            )
            tsum = 0
            for y in range(boardsize):
                for x in range(boardsize):
                    tsum += t[y][x]
                    if t[y][x] >= 100:
                        pointsB[t[y][x] / 100 - 1].append(xy2str(x, y))
                    elif t[y][x] <= -100:
                        pointsW[-t[y][x] / 100 - 1].append(xy2str(x, y))
                    else:
                        pointsM.append(xy2str(x, y))
            s = ""
            for i in range(10):
                if pointsB[i]:
                    s += f"COLOR #{int(25.5 * (i + 1) + 12.8 * (9 - i)):02X}{int(0 * (i + 1) + 12.8 * (9 - i)):02X}{int(0 * (i + 1) + 12.8 * (9 - i)):02X} {' '.join(pointsB[i])}\n"
                if pointsW[i]:
                    s += f"COLOR #{int(0 * (i + 1) + 12.8 * (9 - i)):02X}{int(25.5 * (i + 1) + 12.8 * (9 - i)):02X}{int(0 * (i + 1) + 12.8 * (9 - i)):02X} {' '.join(pointsW[i])}\n"
            if pointsM:
                s += f"COLOR #{128:02X}{128:02X}{128:02X} {' '.join(pointsM)}\n"
            s += f"TEXT {tsum / 1000.0 - komi[0]:.1f}"
            reply("\n" + s.strip())
            continue

        if cmd in [["analyze_black"], ["analyze_white"]]:
            c = 2 if cmd == ["analyze_black"] else 1
            if zenGetNextColor() != c:
                reply("")
                continue
            k = zenGetPolicyKnowledge()
            points = [[], [], [], [], [], [], [], [], [], [], []]
            labels = []
            for y in range(boardsize):
                for x in range(boardsize):
                    if k[y][x] > 200:
                        points[k[y][x] / 100].append(xy2str(x, y))
                        labels.append(xy2str(x, y))
            reply(
                "\n"
                + "\n".join([f"LABEL {item} {item}" for item in labels])
                + "\n"
                + "\n".join(
                    [
                        f"COLOR #{int(25.5 * (c - 1) * i + 12.8 * (10 - i)):02X}{int(25.5 * (2 - c) * i + 12.8 * (10 - i)):02X}{int(12.8 * (10 - i)):02X} {' '.join(points[i])}"
                        for i in range(11)
                        if points[i]
                    ]
                )
            )

            if [
                1 for i in range(len(moves)) if i % 2 == 1 and moves[i] != "PASS"
            ] == []:
                continue

            th = threading.Thread(target=zenGenMove, args=(c, k, 1))
            th.setDaemon(True)
            th.start()
            continue

        reply("")

    output.close()
    wx.Exit()


if len(args) == 0:
    th = threading.Thread(target=gtp_mode)
    th.setDaemon(True)
    th.start()
else:
    if len(args) == 3 and args[0] in ["analyze_black", "analyze_white"]:
        th = threading.Thread(target=analysis_mode)
        th.setDaemon(True)
        th.start()
    else:
        wx.Exit()

app.MainLoop()
