#! /usr/bin/env python
# -*- coding: utf-8 -*-


#################################
#
#   MAIN 
#
#################################
if  __name__ == "__main__":
    
    import argparse
    from pysedm.script.ccd_to_cube import *

    # ================= #
    #   Options         #
    # ================= #
    parser = argparse.ArgumentParser(
        description="""pysedm pipeline to build the cubebuilder objects
            """, formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument('infile', type=str, default=None,
                        help='The date YYYYMMDD')

    parser.add_argument('--rebuild',  action="store_true", default=False,
                        help='If the object you want to build already exists, nothing happens except if this is set')
    
    # --------------- #
    #  Cube Building  #
    # --------------- #
    parser.add_argument('--build',  type=str, default=None,
                        help='Build a e3d cube of the given target or target list (csv) e.g. --build dome or --build dome,Hg,Cd')

    parser.add_argument('--buildbkgd',  type=str, default=None,
                        help='Build a ccd background of the given target or target list (csv) e.g. --build dome or --build dome,Hg,Cd')
    
    # - Trace Matching
    parser.add_argument('--tracematch', action="store_true", default=False,
                        help='build the tracematch solution for the given night. This option saves masks (see tracematchnomasks)')
    
    parser.add_argument('--tracematchnomasks', action="store_true", default=False,
                        help='build te tracematch solution for the given night without saved the masks')
    
    # - Hexagonal Grid
    parser.add_argument('--hexagrid', action="store_true", default=False,
                        help='build the hexagonal grid (index<->qr<->xy) for the given night')

    # - Wavelength Solution
    parser.add_argument('--wavesol', action="store_true", default=False,
                        help='build the wavelength solution for the given night.')
    
    parser.add_argument('--wavesoltest', type=str, default="None",
                        help='to be used with --wavesol. By setting --wavesoltest N one N random wavelength solution will be performed.')
    
    # ----------------- #
    #  Raw Calibration  #
    # ----------------- #
    parser.add_argument('--flat',    action="store_true", default=False,
                        help='Build the flat fielding for the night [see flatref to the reference object]')

    parser.add_argument('--flatref',  type=str, default="dome",
                        help='Build the flat fielding for the night ')
    
    parser.add_argument('--flatlbda',  type=str, default="7000,9000",
                        help='The wavelength range for the flat field. Format: min,max [in Angstrom] ')
    

    # ----------------- #
    #  Short Cuts       #
    # ----------------- #
    parser.add_argument('--allcalibs', action="store_true", default=False,
                        help='')
    
    parser.add_argument('--allscience', action="store_true", default=False,
                        help='')

    parser.add_argument('--nofig',    action="store_true", default=False,
                        help='')

    args = parser.parse_args()
    
    # ================= #
    #   The Scripts     #
    # ================= #
    # --------- #
    #  Date     #
    # --------- #
    date = args.infile

    # ------------ #
    # Short Cuts   #
    # ------------ #
    if args.allcalibs:
        args.tracematch = True
        args.hexagrid   = True
        args.wavesol    = True
        args.build      = "dome"
        args.flat       = True

        
    # ================= #
    #   Actions         #
    # ================= #
    
    # - Builds
    
    if args.buildbkgd is not None and len(args.build) >0:
        for target in args.build.split(","):
            build_night_cubes(date, target=target,
                            lamps=True, only_lamps=True, skip_calib=True, no_bkgd_sub=False,
                            test=None, notebook=False)
    if args.buildbkgd is not None and len(args.buildbkgd) > 0:
        for target in args.buildbkgd.split(","):
            build_backgrounds(date, target=target,
                            lamps=True, only_lamps=True, skip_calib=True, 
                            notebook=False)
        
    # -----------
    # 
    # ----------- 
    # - TraceMatch
    if args.tracematch or args.tracematchnomasks:
        build_tracematcher(date, save_masks=args.tracematch,
                            rebuild_nightly_trace=True, notebook=False, rebuild=args.rebuild)
        
    # - Hexagonal Grid        
    if args.hexagrid:
        build_hexagonalgrid(date)
        
    # - Wavelength Solution
    if args.wavesol:
        ntest = None if "None" in args.wavesoltest else int(args.wavesoltest)
        
        build_wavesolution(date, ntest=ntest, use_fine_tuned_traces=False,
                       lamps=["Hg","Cd","Xe"], saveindividuals=False,
                        savefig=~args.nofig, rebuild=args.rebuild)

    # - Flat Fielding
    if args.flat:
        lbda_min,lbda_max = np.asarray(args.flatlbda.split(","), dtype="float")
        build_flatfield(date,
                        lbda_min=lbda_min,
                        lbda_max=lbda_max, ref=args.flatref,
                        savefig=~args.nofig)

    