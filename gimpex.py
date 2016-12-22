import argparse
import inspect
import subprocess
import re


def main():
    launch_gimp()


def gimp_cbk(cmd, args, flist):
    debug = args['debug']

    def png_save(img, layer, dest, name):
        extra_args = {
            'interlace': 0,
            'compression': 9,
            'bkgd': 1,
            'gama': 0,
            'offs': 0,
            'phys': 1,
            'time': 1,
            'comment': 1,
            'svtrans': 0
            }

        pdb.file_png_save2(img, layer, dest, name, *extra_args.values())

    def jpeg_save(img, layer, dest, name):
        extra_args = {
            'quality': 0.95,
            'smoothing': 0,
            'optimize': 1,
            'progressive': 1,
            'comment': 1,
            'subsmp': 0,
            'baseline': 0,
            'restart': 0,
            'dct': 1
        }

        pdb.file_jpeg_save(img, layer, dest, name, *extra_args.values())

    supported_types = {
        'png': {'save': png_save},
        'jpeg': {'save': jpeg_save},
        'jpg': {'save': jpeg_save},
    }

    def get_ext(f):
        from os import path

        name = path.split(path.normpath(f))[-1]

        ext = path.splitext(name)[1]
        if ext and ext[0] == '.':
            ext = ext[1:]

        return ext.lower()

    def get_base(f):
        from os import path

        name = path.split(path.normpath(f))[1]

        return path.splitext(name)[0]

    def do_import(src, dst):
        fn = get_base(src)
        fe = get_ext(src)
        
        if not supported_types.has_key(fe):
            print 'Input format {} not supported.'.format(fe)
            return
        
        load_func = getattr(pdb, 'file_{}_load'.format(fe))

        img = load_func(src, fn)
        try:
            layer = pdb.gimp_image_merge_visible_layers(img, 1)
            pdb.gimp_file_save(img, layer, dst, fn)
        finally:
            gimp.delete(img)
        
    def do_export(src, dst):
        fn = get_base(src)
        ftype = get_ext(dst)

        finfo = supported_types.get(ftype)

        if not finfo:
            print 'Output format {} not supported.'.format(ftype)
            return

        img = pdb.gimp_file_load(src, fn)

        try:
            layer = pdb.gimp_image_merge_visible_layers(img, 1)

            fsave = finfo['save']
            fsave(img, layer, dst, fn)
        finally:
            gimp.delete(img)
    
    try:
        if cmd == 'export':
            for fin, fout in flist:
                print('Exporting {}=>{}'.format(fin, fout))

                do_export(fin, fout)
        elif cmd == 'import':
            for fin, fout in flist:
                print('Importing {}=>{}'.format(fin, fout))

                do_import(fin, fout)
            
    except KeyboardInterrupt:
        print 'User interrupted.'
    except Exception as e:
        import traceback

        if debug:
            print traceback.print_exc()
        else:
            print 'Operation not completed (pass -d / ' \
                  '--debug switch to see more details)'
    finally:
        pdb.gimp_quit(0)


def launch_gimp():
    args, flist = parse()
    if not flist:
        return

    batch = craft_batch(args, flist)
    subprocess.call(['gimp', '--no-interface',
                     '--batch-interpreter', 'python-fu-eval',
                     '--batch', batch])


def craft_batch(args, flist):
    lines = inspect.getsourcelines(gimp_cbk)[0][1:]
    lines = [re.sub(r'^\s{4}', '', l) for l in lines]

    lines.insert(0, 'cmd = {}\n'.format(repr(args.cmd)))
    lines.insert(1, 'args = {}\n'.format(repr({'debug': args.debug})))
    lines.insert(2, 'flist = {}\n'.format(repr(flist)))

    return ''.join(lines)


def parse():
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--debug', dest='debug', action='store_const',
                        const=True, help='enable debugging')

    children = parser.add_subparsers()
    exp = children.add_parser('export', help='Export .xcf to various formats (jpeg, png)')
    exp.add_argument('-i', '--input', dest='input', action='append')
    exp.add_argument('-o', '--output', dest='output', action='append')
    exp.set_defaults(cmd='export')
    
    imp = children.add_parser('import', help='Import .xcf from various formats (jpeg, png')
    imp.add_argument('-i', '--input', dest='input', action='append')
    imp.add_argument('-o', '--output', dest='output', action='append')
    imp.set_defaults(cmd='import')
    
    args = parser.parse_args()
    
    if not args.input or not args.output \
            or len(args.input) != len(args.output):
        parser.error('Wrong number of arguments')
        return

    return args, zip(args.input, args.output)

main()

