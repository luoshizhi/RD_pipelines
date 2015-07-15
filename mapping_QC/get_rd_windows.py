import argparse
import tables
import matplotlib.pyplot as plt

def calc_n_windows(contig_length, wnd_slide):
    return contig_length / wnd_slide + 1

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("wssd_file")
    parser.add_argument("chr")
    parser.add_argument("outfile")
    parser.add_argument("--start", default=0)
    parser.add_argument("--end", default=-1)
    parser.add_argument("--window_size", default=1000000)
    parser.add_argument("--window_slide", default=200000)
    parser.add_argument("--corrected", action="store_true")

    args = parser.parse_args()

    if args.corrected:
        root = "depthAndStarts_wssd.combined_corrected"
    else:
        root = "depthAndStarts_wssd"

    wssd = tables.File(args.wssd_file, "r")
    contig_rd = wssd.getNode("/%s/%s" % (root, args.chr))[args.start:args.end]
    n_windows = calc_n_windows(contig_rd.shape[0], args.window_slide)
    rds = []
    for i in range(n_windows):
        wnd_start = i * args.window_slide
        wnd_end = wnd_start + args.window_size
        if wnd_end > contig_rd.shape[0]:
            wnd_end = contig_rd.shape[0]
        window_rd = contig_rd[i * args.window_slide : wnd_end][:, :, 0].sum()
        rds.append(window_rd / float(wnd_end - wnd_start))
    axes = plt.figure().add_subplot(111)
    plt.plot(rds)
    sample = args.wssd_file.split("/")[-2]
    plt.title("%s %s" % (sample, args.chr))
    ticks = axes.get_xticks().tolist()
    tick_labels = map(lambda x: round(x * args.window_slide/1000000., 2), ticks)
    plt.xticks(ticks, tick_labels)
    plt.xlabel("Position (Mb)")
    plt.ylabel("Read depth")
    plt.savefig(args.outfile)
