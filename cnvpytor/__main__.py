"""
__main__

"""
from __future__ import print_function
from .__init__ import *
import sys
import logging
import argparse
import matplotlib.pyplot as plt

__version__ = '1.0a1'


def main():
    """ main()
    CNVpytor main commandline program.

    """
    parser = argparse.ArgumentParser(
        description="Lite version of the CNVnator written in Python.\nA tool for CNV discovery from depth of read mapping.")
    parser.add_argument('-version', '--version', action='store_true', help='show version number and exit')
    parser.add_argument('-root', '--root', type=str, nargs="+",
                        help="CNVnator hd5 file: data storage for all calculations", default=None)
    parser.add_argument('-ls', '--ls', action='store_true', help='list CNVnator file(s) content')
    parser.add_argument('-chrom', '--chrom', type=str, nargs="+", help="list of chromosomes to apply calculation",
                        default=[])
    parser.add_argument('-v', '--verbose', type=str,
                        choices=["none", "debug", "info", "warning", "error", "d", "e", "i", "w"],
                        help="verbose level: debug, info (default), warning, error", default="info")
    parser.add_argument('-log', '--log_file', type=str, help='log file')
    parser.add_argument('-j', '--max_cores', type=int,
                        help="maximal number of cores to use in calculation", default=8)
    parser.add_argument('-rd', '--rd', nargs="+", type=str, help="read bam/sam/cram and store read depth information")
    parser.add_argument('-gc', '--gc', type=str, help="read fasta file and store GC/AT content")
    parser.add_argument('-cgc', '--copy_gc', type=str, help="copy GC/AT content from another cnvnator file")
    parser.add_argument('-his', '--his', type=binsize_type, nargs="+",
                        help="create histograms for specified bin size (multiple bin sizes separate by space)")
    parser.add_argument('-stat', '--stat', type=binsize_type, nargs="+",
                        help="calculate statistics for specified bin size (multiple bin sizes separate by space)")
    parser.add_argument('-partition', '--partition', type=binsize_type, nargs="+",
                        help="calculate segmentation for specified bin size (multiple bin sizes separate by space)")
    parser.add_argument('-call', '--call', type=str, nargs="+",
                        help="CNV caller: [baf] bin_size [bin_size2 ...] (multiple bin sizes separate by space)")
    parser.add_argument('-vcf', '--vcf', nargs="+", type=str, help="read SNP data from vcf files")
    parser.add_argument('-pileup', '--pileup_bam', nargs="+", type=str, help="calculate SNP counts from bam files")

    parser.add_argument('-mask', '--mask', type=str, help="read fasta mask file and flag SNPs in P region")
    parser.add_argument('-mask_snps', '--mask_snps', action='store_true', help="flag SNPs in P region")
    parser.add_argument('-idvar', '--idvar', type=str, help="read vcf file and flag SNPs that exist in database file")
    parser.add_argument('-baf', '--baf', type=binsize_type, nargs="+",
                        help="create BAF histograms for specified bin size (multiple bin sizes separate by space)")
    parser.add_argument('-nomask', '--no_mask', action='store_true', help="do not use P mask in BAF histograms")
    parser.add_argument('-useid', '--use_id', action='store_true', help="use id flag filtering in SNP histograms")



    parser.add_argument('-plot', '--plot', type=str, nargs="+", help="plotting")
    parser.add_argument('-view', '--view', type=binsize_type,
                        help="Enters interactive ploting mode")
    parser.add_argument('-panels', '--panels', type=str, nargs="+", default=["rd"], choices=["rd", "baf", "likelihood"],
                        help="plot panels (with -plot regions)")

    parser.add_argument('-style', '--plot_style', type=str,
                        help="available plot styles: " + ", ".join(plt.style.available), choices=plt.style.available)
    parser.add_argument('-o', '--plot_output_file', type=str, help="output filename prefix and extension", default="")
    parser.add_argument('-anim', '--animation', type=str, help="animation folder/prefix", default="")

    parser.add_argument('-make_gc_file', '--make_gc_genome_file', action='store_true',
                        help="used with -gc will create genome gc file")
    parser.add_argument('-make_mask_file', '--make_mask_genome_file', action='store_true',
                        help="used with -mask will create genome mask file")
    parser.add_argument('-use_mask_rd', '--use_mask_with_rd', action='store_true', help="used P mask in RD histograms")
    parser.add_argument('-rg', '--reference_genome', type=str, help="Manually set reference genome", default=None)
    parser.add_argument('-sample', '--vcf_sample', type=str, help="Sample name in vcf file", default="")
    parser.add_argument('-conf', '--reference_genomes_conf', type=str, help="Configuration with reference genomes", default=None)

    args = parser.parse_args(sys.argv[1:])

    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    if args.verbose in {"debug", "d"}:
        level = logging.DEBUG
    elif args.verbose in {"info", "i"}:
        level = logging.INFO
    elif args.verbose in {"warning", "w"}:
        level = logging.WARNING
    elif args.verbose in {"error", "e"}:
        level = logging.ERROR
    else:
        level = logging.CRITICAL

    if args.log_file:
        logging.basicConfig(filename=args.log_file, level=logging.DEBUG, format=log_format)
        logger = logging.getLogger('cnvpytor')
        ch = logging.StreamHandler()
        formatter = logging.Formatter(log_format)
        ch.setFormatter(formatter)
        ch.setLevel(level)
        logger.addHandler(ch)
    else:
        logging.basicConfig(level=level, format=log_format)
        logger = logging.getLogger('cnvpytor')
    logger.debug("Start logging...")


    if args.version:
        print('pyCNVnator {}'.format(__version__))
        return 0

    if args.reference_genomes_conf:
        Genome.load_reference_genomes(args.reference_genomes_conf)

    if args.root is not None:

        if args.ls:
            app = Root(args.root[0], max_cores=args.max_cores)
            app.ls()

        if args.reference_genome:
            app = Root(args.root[0], max_cores=args.max_cores)
            app.set_reference_genome(args.reference_genome)

        if args.rd:
            app = Root(args.root[0], max_cores=args.max_cores)
            app.rd(args.rd, chroms=args.chrom)

        if args.plot:
            view = Viewer(args.root, args.plot_output_file)
            if args.plot_style:
                view.set_style(args.plot_style)
            view.plot(args)

        if args.view:
            view = Viewer(args.root, args.plot_output_file)
            if args.plot_style:
                view.set_style(args.plot_style)
            view.prompt(args.view, args)

        if args.gc:
            app = Root(args.root[0], max_cores=args.max_cores)
            app.gc(args.gc, chroms=args.chrom, make_gc_genome_file=args.make_gc_genome_file)

        if args.copy_gc:
            app = Root(args.root[0], max_cores=args.max_cores)
            app.copy_gc(args.copy_gc, chroms=args.chrom)

        if args.vcf:
            app = Root(args.root[0], max_cores=args.max_cores)
            app.vcf(args.vcf, chroms=args.chrom, sample=args.vcf_sample)

        if args.pileup_bam:
            app = Root(args.root[0], max_cores=args.max_cores)
            app.pileup(args.pileup_bam, chroms=args.chrom)

        if args.mask:
            app = Root(args.root[0], max_cores=args.max_cores)
            app.mask(args.mask, chroms=args.chrom, make_mask_genome_file=args.make_mask_genome_file)

        if args.mask_snps:
            app = Root(args.root[0], max_cores=args.max_cores)
            app.mask_snps()

        if args.stat:
            app = Root(args.root[0], max_cores=args.max_cores)
            app.rd_stat(chroms=args.chrom)

        if args.his:
            app = Root(args.root[0], max_cores=args.max_cores)
            app.calculate_histograms(args.his, chroms=args.chrom)

        if args.baf:
            app = Root(args.root[0], max_cores=args.max_cores)
            app.calculate_baf(args.baf, chroms=args.chrom, use_id=args.use_id, use_mask=not args.no_mask)

        if args.call:
            app = Root(args.root[0], max_cores=args.max_cores)
            if args.call[0] == "baf":
                app.call_baf([binsize_type(x) for x in args.call[1:]], chroms=args.chrom, use_id=args.use_id,
                             use_mask=not args.no_mask, anim=args.animation)


if __name__ == '__main__':
    main()
