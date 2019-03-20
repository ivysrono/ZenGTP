import os, sys

name = os.path.basename(sys.argv[0]).split(".")[0].split("-")[0]  # 获取生成的 exe 文件名并处理
version = "Py372"
program = name + "-" + version
logfile = ""
threads = int(os.environ["NUMBER_OF_PROCESSORS"])
boardsize = 19
maxtime = 1000000000.0
moves = []
prefix = {}

"""
if "6" in name:
if "7" in name:
"""

if "6" in name:
    book = {
        "19": ["Q16", "R16"],
        "19 Q16": ["D16", "D4"],
        "19 R16": ["D16", "D17", "D4", "Q4"],
    }
    komi = [7.5, -7.5]
    weight = 0.5
    qparm = 200
if "7" in name:
    book = {}
    komi = [7.5, 50.0, 0.0]
    weight = [0.75, 0.75]
    qparm = [0, 0]


dirname = os.path.dirname(sys.argv[0])
dirname += "\\" if dirname and dirname[-1] != "\\" else ""


def help():  # .ljust 为字符串左对齐方法
    # show(f"{name} allowed options:")
    if "6" in name:
        show("Zen6GTP allowed options:")
        show(
            " -M [ --maxcount ] num".ljust(25)
            + "Set the max count for top moves. (30000)"
        )
        show(" -m [ --mincount ] num".ljust(25) + "Set the min count for good moves.")
    if "7" in name:
        show("Zen7GTP allowed options:")
        show(" -S [ --strength ] num".ljust(25) + "Set the playing strength.")
    show(" -h [ --help ]".ljust(25) + "Show all allowed options.")
    show(" -l [ --logfile ] file".ljust(25) + "Set the log file.")
    show(" -t [ --threads ] num".ljust(25) + "Set the number of threads to use.")
    show(" -T [ --maxtime ] num".ljust(25) + "Set the max time for one move.")
    sys.exit()


def bw2int(s):
    return 1 if s in ["W", "w"] else 2


def int2bw(c):
    return "W" if c == 1 else "B"


def str2xy(m):
    return "ABCDEFGHJKLMNOPQRSTUVWXYZ".find(m[0].upper()), boardsize - int(m[1:])


def xy2str(x, y):
    return "ABCDEFGHJKLMNOPQRSTUVWXYZ"[x] + str(boardsize - y)


def reply(s):
    sys.stdout.write("= " + s + "\n\n")
    sys.stdout.flush()


def show(s):
    sys.stderr.write(s + "\n")
    sys.stderr.flush()


def transform(m, n):
    if m == "PASS":
        return "PASS"
    x, y = str2xy(m)
    if n == 0:
        return m
    if n == 1 or n == -1:
        return xy2str(x, boardsize - 1 - y)
    if n == 2 or n == -2:
        return xy2str(boardsize - 1 - x, y)
    if n == 3 or n == -3:
        return xy2str(boardsize - 1 - x, boardsize - 1 - y)
    if n == 4 or n == -4:
        return xy2str(y, x)
    if n == 5 or n == -6:
        return xy2str(boardsize - 1 - y, x)
    if n == 6 or n == -5:
        return xy2str(y, boardsize - 1 - x)
    if n == 7 or n == -7:
        return xy2str(boardsize - 1 - y, boardsize - 1 - x)


def isBookDatExist(dirname):
    if os.path.exists(dirname + "book.dat"):
        try:
            data = open(dirname + "book.dat", "r")
        except IOError:
            show("Failed to open the book file book.dat.")
            sys.exit()
        while True:
            line = data.readline()
            if line == "":
                break
            line = line.strip()
            if line == "" or line[0] == "#":
                continue
            l = line.split("|")
            if len(l) > 2:
                continue
            if len(l) == 2:
                game, move = l[0].strip(), l[1].strip()
                g = game.split()
                m = move.split()
                if g[0].isdigit():
                    for mm in m:
                        if game in book:
                            if not mm in book[game]:
                                book[game].append(mm)
                        else:
                            book[game] = [mm]
                else:
                    if g[0] in prefix:
                        for g0 in prefix[g[0]]:
                            g1 = (f"{g0} {' '.join(g[1:])}").strip()
                            for mm in m:
                                if g1 in book:
                                    if not mm in book[g1]:
                                        book[g1].append(mm)
                                else:
                                    book[g1] = [mm]
                continue
            l = line.split(":")
            if len(l) != 2:
                continue
            ngame, game = l[0].strip(), l[1].strip()
            if len(ngame.split()) > 1:
                continue
            g = game.split()
            if g[0].isdigit():
                if ngame in prefix:
                    if not game in prefix[ngame]:
                        prefix[ngame].append(game)
                else:
                    prefix[ngame] = [game]
            else:
                if g[0] in prefix:
                    for g0 in prefix[g[0]]:
                        g1 = (f"{g0} {' '.join(g[1:])}").strip()
                        if ngame in prefix:
                            if not g1 in prefix[ngame]:
                                prefix[ngame].append(g1)
                        else:
                            prefix[ngame] = [g1]
        data.close()
