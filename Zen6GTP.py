from generalFunctions import *
from ctypes import *
import sys, os, time, getopt, random, subprocess, threading

##################################################

# 以下为 Zen6GTP 专用变量
maxcount = 30000
mincount = -1
above = -1
maxnum = 1000000000
sparm = [0.25, 0.25]
pwfactor = 1.1
verbose = False

################################################

try:
    opts, args = getopt.getopt(
        sys.argv[1:],
        'ht:T:M:m:l:k:w:n:a:s:f:vq:',
        ['help', 'threads=', 'maxtime=', 'maxcount=', 'mincount=', 'logfile='],
    )
except getopt.GetoptError:
    help()
if args != []:
    help()

for opt, arg in opts:
    if opt in ['-h', '--help']:
        help()
    if opt in ['-t', '--threads']:
        if not arg.isdigit() or int(arg) < 1:
            help()
        threads = int(arg)
        continue
    if opt in ['-T', '--maxtime']:
        maxtime = float(arg)
        continue
    if opt in ['-M', '--maxcount']:
        if not arg.isdigit() or int(arg) < 1:
            help()
        maxcount = int(arg)
        continue
    if opt in ['-m', '--mincount']:
        if not arg.isdigit() or int(arg) < 1:
            help()
        mincount = int(arg)
        continue
    if opt in ['-l', '--logfile']:
        logfile = arg
        continue
    if opt in ['-k']:
        komi[1] = float(arg)
        continue
    if opt in ['-w']:
        weight = float(arg)
        continue
    if opt in ['-n']:
        maxnum = int(arg)
        continue
    if opt in ['-a']:
        above = int(arg)
        continue
    if opt in ['-s']:
        s0, s1 = arg.split(',')
        sparm[0] = float(s0)
        sparm[1] = float(s1)
        continue
    if opt in ['-f']:
        pwfactor = float(arg)
        continue
    if opt in ['-v']:
        verbose = True
        continue
    if opt in ['-q']:
        qparm = float(arg) * 1000
        if qparm > 1000 or qparm < 0:
            help()
        continue

if mincount > maxcount:
    help()
if mincount == -1:
    mincount = int(maxcount * 0.4)
if above >= mincount:
    help()
if above == -1:
    above = int(mincount * 0.05)

# 以下将 log 置于 logs 文件夹内的方法来自 Zen7GTP，很奇怪不能抽离
if logfile == '':
    if os.path.exists(dirname + 'logs'):
        if not os.path.isdir(dirname + 'logs'):
            help()
    else:
        try:
            os.mkdir(dirname + 'logs')
        except WindowsError:
            help()
    logfile = dirname + 'logs\\' + time.strftime('%Y%m%d-%H%M%S') + '.log'

try:
    output = open(logfile, 'w')
except IOError:
    help()
output.write('=== ' + program + ' ===\n\n')
output.flush()


def log(s):
    if logfile != '':
        output.write(f'[{len(moves):03}] {s}\n')
        output.flush()


isBookDatExist(dirname)

try:
    zen = CDLL(dirname + 'Zen.dll')
except WindowsError:
    show('Zen.dll is missing.')
    sys.exit()
try:
    leela = subprocess.Popen(
        [dirname + 'Leela0100GTP.exe', '-g', '-q'],
        universal_newlines=True,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
except WindowsError:
    show('Leela0100GTP.exe is missing.')
    sys.exit()

# zenClearBoard = zen[2]
zenGetNextColor = zen[7]
zenGetNumBlackPrisoners = zen[8]
zenGetNumWhitePrisoners = zen[9]
# zenGetPriorKnowledge = zen[10]
# zenGetTopMoveInfo = zen[12]
zenInitialize = zen[13]
zenIsLegal = zen[15]
zenIsThinking = zen[17]
# zenPass = zen[19]
# zenPlay = zen[20]
zenSetAmafWeightFactor = zen[22]
# zenSetBoardSize = zen[23]
zenSetDCNN = zen[24]
# zenSetKomi = zen[25]
zenSetMaxTime = zen[26]
zenSetNumberOfSimulations = zen[28]
zenSetNumberOfThreads = zen[29]
zenSetPriorWeightFactor = zen[30]
zenStartThinking = zen[31]
zenStopThinking = zen[32]

# zenUndo = zen[35]


def zenClearBoard():
    global moves
    if len(moves) > 0 and logfile != '':
        output.write('=== End ===\n\n')
        output.flush()
    moves = []
    zen[2]()
    leela.stdin.write('clear_board\n')
    leela.stdin.flush()
    leela.stdout.readline()
    leela.stdout.readline()


def zenGetPriorKnowledge():
    k = ((c_int * 19) * 19)()
    zen[10](k)
    return k


def zenGetTerritoryStatictics():
    t = ((c_int * 19) * 19)()
    zen[11](t)
    return t


def zenGetTopMoveInfo(n):
    x, y, p, w, s = c_int(0), c_int(0), c_int(0), c_float(0), create_string_buffer(100)
    zen[12](n, byref(x), byref(y), byref(p), byref(w), s, 99)
    return x.value, y.value, p.value, w.value, s.value.decode().rstrip()


def zenGetNetWin(c, l):
    n, vn, vn2 = len(l), [], []
    for i in range(n):
        x, y = -1, -1
        if l[i].lower() == 'pass':
            zen[19](c)
        else:
            x, y = str2xy(l[i])
            zen[20](x, y, c)
        v = 1.0
        if i % 2 == 0:
            kk = zenGetPriorKnowledge()
        else:
            for yy in range(boardsize):
                for xx in range(boardsize):
                    if (xx != x or yy != y) and kk[yy][xx] > 500:
                        leela.stdin.write(f'play {int2bw(c)} {xy2str(xx, yy)}\n')
                        leela.stdin.flush()
                        leela.stdout.readline()
                        leela.stdout.readline()
                        leela.stdin.write('vn_winrate\n')
                        leela.stdin.flush()
                        v = min(v, float(leela.stdout.readline().split()[1]))
                        leela.stdout.readline()
                        leela.stdin.write('undo\n')
                        leela.stdin.flush()
                        leela.stdout.readline()
                        leela.stdout.readline()
        vn2.append(v)
        leela.stdin.write(f'play {int2bw(c)} {l[i]}\n')
        leela.stdin.flush()
        leela.stdout.readline()
        leela.stdout.readline()
        leela.stdin.write('vn_winrate\n')
        leela.stdin.flush()
        vn.append(1 - (i % 2) + ((i % 2) * 2 - 1) * float(leela.stdout.readline().split()[1]))
        leela.stdout.readline()
        c = 3 - c
    netwin = vn[-1]
    zen[35](n)
    for i in range(n):
        leela.stdin.write('undo\n')
        leela.stdin.flush()
        leela.stdout.readline()
        leela.stdout.readline()
        if vn[n - 1 - i] > netwin:
            netwin = min(sparm[0] * vn[n - 1 - i] + (1 - sparm[0]) * netwin, vn2[n - 1 - i])
        else:
            netwin = min(sparm[1] * vn[n - 1 - i] + (1 - sparm[1]) * netwin, vn2[n - 1 - i])
    return netwin


vncache = {}


def zenGetNetWin2(c, m):
    global vncache
    if m in vncache:
        return vncache[m]
    leela.stdin.write(f'play {int2bw(c)} {m}\n')
    leela.stdin.flush()
    leela.stdout.readline()
    leela.stdout.readline()
    leela.stdin.write('vn_winrate\n')
    leela.stdin.flush()
    netwin = 1 - float(leela.stdout.readline().split()[1])
    leela.stdout.readline()
    leela.stdin.write('undo\n')
    leela.stdin.flush()
    leela.stdout.readline()
    leela.stdout.readline()
    vncache[m] = netwin
    return netwin


def zenPass(c):
    moves.append('PASS')
    zen[19](c)
    leela.stdin.write(f'play {int2bw(c)} PASS\n')
    leela.stdin.flush()
    leela.stdout.readline()
    leela.stdout.readline()


def zenPlay(x, y, c):
    moves.append(xy2str(x, y))
    zen[20](x, y, c)
    leela.stdin.write(f'play {int2bw(c)} {xy2str(x, y)}\n')
    leela.stdin.flush()
    leela.stdout.readline()
    leela.stdout.readline()


def zenSetBoardSize(n):
    zen[23](n)
    leela.stdin.write(f'boardsize {str(n)}\n')
    leela.stdin.flush()
    leela.stdout.readline()
    leela.stdout.readline()


def zenSetKomi(k1, k2):
    zen[25](c_float(k1 + k2))
    leela.stdin.write(f'komi {str(k1)}\n')
    leela.stdin.flush()
    leela.stdout.readline()
    leela.stdout.readline()


def zenUndo(n):
    global moves
    moves = moves[:-n]
    zen[35](n)
    for i in range(n):
        leela.stdin.write('undo\n')
        leela.stdin.flush()
        leela.stdout.readline()
        leela.stdout.readline()


stopThinking = False
isThinking = False


def zenGenMove(c, k, a):
    global vncache
    global isThinking
    isThinking = True

    dykomi = (komi[1] * (1 - len(moves) / 200.0) if boardsize == 19 and len(moves) < 200 else 0)
    zenSetKomi(komi[0], dykomi * (2 * c - 3))

    topA = []
    vncache = {}
    zenStartThinking(c)

    while zenIsThinking() != -0x80000000:
        time.sleep(1.0)

        xylistA, topB, incB = [itemA[0:2] for itemA in topA], [], []
        for n in range(5):
            x, y, p, w, s = zenGetTopMoveInfo(n)
            w = max(0.0, min(1.0, w + dykomi / 150.0))
            if p == 0:
                break
            if [x, y] in xylistA:
                m = xylistA.index([x, y])
                topB.append([
                    x,
                    y,
                    p,
                    w,
                    s,
                    '+' if m > n else '-' if m < n else '=',
                    '+' if p > topA[m][2] else '=',
                    '+' if w > topA[m][3] else '-' if w < topA[m][3] else '=',
                    0 if s.split()[0] == 'pass' else k[y][x],
                    zenGetNetWin2(c,
                                  s.split()[0]),
                ])
                incB.append(p - topA[m][2])
            else:
                topB.append([
                    x,
                    y,
                    p,
                    w,
                    s,
                    '+',
                    '+',
                    '+',
                    0 if s.split()[0] == 'pass' else k[y][x],
                    zenGetNetWin2(c,
                                  s.split()[0]),
                ])
                incB.append(p)
        if incB and max(incB) > 0:
            topB[incB.index(max(incB))][6] = '#'

        xylistB = [itemB[0:2] for itemB in topB]
        for itemA in topA:
            if not itemA[0:2] in xylistB:
                itemA[5], itemA[6], itemA[7] = '?' if itemA[6] == '?' else '-', '?', '?'
                topB.append(itemA)

        if topB and topB != topA:
            topA = topB
            show(  # GTP Shell
                '\n' + '\n'.join([(f'   {int2bw(c)} '
                                   f'{itemB[4].split()[0]:<4}'
                                   f'[{itemB[5]}] '
                                   '-> '
                                   f'{itemB[2]:>8} '
                                   f'[{itemB[6]}], '
                                   f'{itemB[3]:>6.2%} '
                                   f'[{itemB[7]}], '
                                   f'{itemB[9]:>6.2%}, '
                                   f'{itemB[8] / 1000.0:.3f}, '
                                   f'{itemB[4]}') for itemB in topB]))
            if (a == 0 and
                (topB[0][2] > maxcount or time.time() - time0 + 1.0 > maxtime or
                 (topB[0][2] >= mincount and max([itemB[2]
                                                  for itemB in topB[1:] if itemB[2] < mincount] + [0]) < above))) or (
                                                      a == 1 and stopThinking):
                break

    show('')
    if zenIsThinking() != -0x80000000:
        show((f'   Komi:       '
              f'{komi[0]:.1f}'
              f'{" + " if dykomi * (2 * c - 3) >= 0 else " - "}'
              f'{abs(dykomi):.1f}'))
        zenStopThinking()
        show('')
    isThinking = False
    return topA


zenInitialize('')
zenSetBoardSize(boardsize)
zenSetNumberOfThreads(threads)
zenSetNumberOfSimulations(1000000000)
zenSetMaxTime(c_float(1000000000.0))
zenSetAmafWeightFactor(c_float(pwfactor))
zenSetPriorWeightFactor(c_float(1.0))
zenSetDCNN(True)
zenClearBoard()

while True:
    cmd = input('').lower().split()
    time0 = time.time()
    stopThinking = True
    while isThinking:
        time.sleep(0.1)
    stopThinking = False

    if cmd == ['list_commands']:
        reply('\n'.join([
            'list_commands',
            'name',
            'version',
            'protocol_version',
            'quit',
            'clear_board',
            'boardsize',
            'komi',
            'undo',
            'gg-undo',
            'pass',
            'play',
            'genmove',
            'genbook',
            'gogui-analyze_commands',
            'prior_knowledge',
            'territory_statictics',
            'analyze_black',
            'analyze_white',
        ]))
        continue

    if cmd == ['name']:
        reply(name)
        continue

    if cmd == ['version']:
        reply(version)
        continue

    if cmd == ['protocol_version']:
        reply('2')
        continue

    if cmd == ['quit']:
        break

    if cmd == ['clear_board']:
        reply('')
        zenClearBoard()
        continue

    if cmd[:-1] == ['boardsize'] and cmd[-1].isdigit() and 0 < int(cmd[-1]) <= 19:
        reply('')
        boardsize = int(cmd[-1])
        zenSetBoardSize(boardsize)
        continue

    if cmd[:-1] == ['komi']:
        reply('')
        komi[0] = float(cmd[-1])
        continue

    if cmd == ['undo'] and len(moves) > 0:
        reply('')
        zenUndo(1)
        continue

    if cmd[:-1] == ['gg-undo'] and cmd[-1].isdigit() and len(moves) >= int(cmd[-1]):
        reply('')
        zenUndo(int(cmd[-1]))
        continue

    if cmd in [['play', 'w', 'pass'], ['play', 'b', 'pass']]:
        reply('')
        c = zenGetNextColor()
        if [c, cmd[1]] in [[1, 'b'], [2, 'w']]:
            zenPass(c)
            log(int2bw(c) + ' pass;')
            c = 3 - c
        zenPass(c)
        log(int2bw(c) + ' pass;')
        continue

    if (cmd[:-1] in [['play', 'w'], ['play', 'b']] and len(cmd[-1]) >= 2
            and cmd[-1][0] in 'abcdefghjklmnopqrstuvwxyz' [0:boardsize] and cmd[-1][1:].isdigit()
            and int(cmd[-1][1:]) in range(1, boardsize + 1)):
        reply('')
        x, y = str2xy(cmd[-1])
        c = zenGetNextColor()
        if [c, cmd[1]] in [[1, 'b'], [2, 'w']]:
            zenPass(c)
            log(int2bw(c) + ' pass;')
            c = 3 - c
        zenPlay(x, y, c)
        log(int2bw(c) + ' ' + cmd[-1].upper() + ';')
        continue

    if cmd == ['genmove', 'white']:
        cmd = ['genmove', 'w']
    if cmd == ['genmove', 'black']:
        cmd = ['genmove', 'b']
    if cmd in [['genmove', 'w'], ['genmove', 'b']]:
        c, k = zenGetNextColor(), zenGetPriorKnowledge()
        if [c, cmd[1]] in [[1, 'b'], [2, 'w']]:
            zenPass(c)
            log(int2bw(c) + ' pass;')
            c = 3 - c
        mlist = []
        for n in range(8):
            game = (str(boardsize) + ' ' + ' '.join([transform(m, n) for m in moves])).strip()
            if game in book:
                for m in book[game]:
                    m = transform(m, -n)
                    x, y = str2xy(m)
                    if not m in mlist and zenIsLegal(x, y, c):
                        mlist.append(m)

        if mlist:
            show((str(boardsize) + ' ' + ' '.join(moves)).strip() + ' | ' + ' '.join(mlist))
            show('')
            m1 = random.sample(mlist, 1)[0]
            x, y = str2xy(m1)
            zenPlay(x, y, c)
            log(
                int2bw(c) + ' ' + m1 + '\n\n' + (str(boardsize) + ' ' + ' '.join(moves[:-1])).strip() + ' | ' +
                ' '.join(mlist) + ';\n')
            reply(m1)
            continue
        xylist = [[x, y] for y in range(boardsize) for x in range(boardsize) if k[y][x] >= qparm]
        if len(xylist) == 1:
            m1 = xy2str(xylist[0][0], xylist[0][1])
            zenPlay(xylist[0][0], xylist[0][1], c)
            log(int2bw(c) + ' ' + m1 + ';')
            reply(m1)
            continue
        ispass, top = True, zenGenMove(c, k, 0)
        if top:
            s = '\n'.join([(f'{int2bw(c)} '
                            f'{item[4].split()[0]:<4}'
                            '-> '
                            f'{item[2]:>8},'
                            f'{item[3]:>6.2%},'
                            f'{item[9]:>6.2%}, '
                            f'{item[8] / 1000.0:.3f}, '
                            f'{item[4]}') for item in top])
            if top[0][4].split()[0].lower() != 'pass':
                ispass = False
                good = [
                    item for item in top if item[2] * maxcount >= top[0][2] *
                    mincount and item[3] > 0.1 and item[4].split()[0].lower() != 'pass'
                ][0:maxnum]
        if ispass == True:
            reply('pass')
            zenPass(c)
            log(int2bw(c) + ' pass;')
            continue
        if good == []:
            reply('resign')
            log(int2bw(c) + ' resign;')
            continue
        l, wins = 0, []
        if boardsize == 19 and (verbose or len(good) > 1):
            s += '\n'
            for item in good:
                mcwin, netwin = item[3], zenGetNetWin(c, item[4].split())
                win = (mcwin * weight) + (netwin * (1 - weight))
                wins.append(win)
                show(  # GTP shell
                    (f'   {int2bw(c)} '
                     f'{item[4].split()[0]:<3}: { win:>6.2%} '
                     f'(MC: {mcwin:>6.2%}, VN: {netwin:>6.2%})'))
                s += (f'\n{int2bw(c)} '
                      f'{item[4].split()[0]:<3}: { win:>6.2%} '
                      f'(MC:{ mcwin:>6.2%}, VN:{ netwin:>6.2%})')
            l = wins.index(max(wins))
            show('')
        m = good[l][4].split()[0]
        x, y = str2xy(m)
        zenPlay(x, y, c)
        log(f'{int2bw(c)} {m}\n\n;\n')
        reply(m)
        continue

    if cmd in [['genbook'], ['genbook', 'w'], ['genbook', 'b']] and moves:
        cc = [0, 1] if len(cmd) == 1 else [1] if cmd[1] == 'w' else [0]
        l = [(f'{(str(boardsize) + " " + " ".join(moves[:i])).strip()}'
              ' | '
              f'{moves[i]}') for i in range(len(moves)) if i % 2 in cc and moves[i] != 'PASS']
        reply('\n' + '\n'.join(l) if l else '')
        continue

    if cmd == ['gogui-analyze_commands']:
        reply('\n'.join([
            'gfx/Prior Knowledge/prior_knowledge',
            'gfx/Territory Statictics/territory_statictics',
            'gfx/Analysis for Black/analyze_black',
            'gfx/Analysis for White/analyze_white',
        ]))
        continue

    if cmd == ['prior_knowledge']:
        c, k = zenGetNextColor(), zenGetPriorKnowledge()
        points = [[], [], [], [], [], [], [], [], [], [], []]
        values = []
        for y in range(boardsize):
            for x in range(boardsize):
                points[max(0, k[y][x]) / 100].append(xy2str(x, y))
                if k[y][x] > 200:
                    leela.stdin.write(f'play {int2bw(c)} {xy2str(x, y)}\n')
                    leela.stdin.flush()
                    leela.stdout.readline()
                    leela.stdout.readline()
                    leela.stdin.write('vn_winrate\n')
                    leela.stdin.flush()
                    values.append([xy2str(x, y), 1 - float(leela.stdout.readline().split()[1])])
                    leela.stdout.readline()
                    leela.stdin.write('undo\n')
                    leela.stdin.flush()
                    leela.stdout.readline()
                    leela.stdout.readline()
        reply('\n' + '\n'.join([(f'COLOR #'
                                 f'{int(25.5 * (c - 1) * i + 12.8 * (10 - i)):02X}'
                                 f'{int(25.5 * (2 - c) * i + 12.8 * (10 - i)):02X}'
                                 f'{int(12.8 * (10 - i)):02X} '
                                 f'{" ".join(points[i])}') for i in range(11) if points[i]]) + '\n' +
              '\n'.join([f'LABEL {item[0]} {item[1] * 100:.1f}' for item in values]))
        continue

    if cmd == ['territory_statictics']:
        t = zenGetTerritoryStatictics()
        pointsW, pointsB, pointsM = (
            [[], [], [], [], [], [], [], [], [], []],
            [[], [], [], [], [], [], [], [], [], []],
            [],
        )
        sum = 0
        for y in range(boardsize):
            for x in range(boardsize):
                sum += t[y][x]
                if t[y][x] >= 100:
                    pointsB[t[y][x] / 100 - 1].append(xy2str(x, y))
                elif t[y][x] <= -100:
                    pointsW[-t[y][x] / 100 - 1].append(xy2str(x, y))
                else:
                    pointsM.append(xy2str(x, y))
        s = ''
        for i in range(10):
            if pointsB[i]:
                s += (f'COLOR #'
                      f'{int(25.5 * (i + 1) + 12.8 * (9 - i)):02X}'
                      f'{int(0 * (i + 1) + 12.8 * (9 - i)):02X}'
                      f'{int(0 * (i + 1) + 12.8 * (9 - i)):02X} '
                      f'{" ".join(pointsB[i])}\n')
            if pointsW[i]:
                s += (f'COLOR #'
                      f'{int(0 * (i + 1) + 12.8 * (9 - i)):02X}'
                      f'{int(25.5 * (i + 1) + 12.8 * (9 - i)):02X}'
                      f'{int(0 * (i + 1) + 12.8 * (9 - i)):02X} '
                      f'{" ".join(pointsW[i])}\n')
        if pointsM:
            s += f'COLOR #{128:02X}{128:02X}{128:02X} {" ".join(pointsM)}\n'
        s += f'TEXT {sum / 1000.0 - komi[0]:.1f}'
        reply('\n' + s.strip())
        continue

    if cmd in [['analyze_black'], ['analyze_white']]:
        c = 2 if cmd == ['analyze_black'] else 1
        if zenGetNextColor() != c:
            reply('')
            continue
        k = zenGetPriorKnowledge()
        points = [[], [], [], [], [], [], [], [], [], [], []]
        labels = []
        for y in range(boardsize):
            for x in range(boardsize):
                if k[y][x] > 200:
                    points[k[y][x] / 100].append(xy2str(x, y))
                    labels.append(xy2str(x, y))
        reply('\n' + '\n'.join([(f'COLOR #'
                                 f'{int(25.5 * (c - 1) * i + 12.8 * (10 - i)):02X}'
                                 f'{int(25.5 * (2 - c) * i + 12.8 * (10 - i)):02X}'
                                 f'{int(12.8 * (10 - i)):02X} '
                                 f'{" ".join(points[i])}') for i in range(11) if points[i]]) + '\n' +
              '\n'.join([f'LABEL {item} {item}' for item in labels]))

        th = threading.Thread(target=zenGenMove, args=(c, k, 1))
        th.setDaemon(True)
        th.start()
        continue

    reply('')

if logfile != '':
    output.close()
