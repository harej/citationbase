import csv, requests, sys, threading
from subprocess import Popen, PIPE, STDOUT, DEVNULL
from time import sleep

class ProcLauncher(threading.Thread):
    def __init__(self, threadID, name, package, url_template, proc_count, step):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.package = package
        self.url_template = url_template
        self.proc_count = proc_count
        self.step = step

    def execute(self, cmd, stdout=PIPE, stderr=STDOUT):
        subproc = Popen(['/bin/bash', '-c', cmd], stdout=stdout, stderr=stderr)
        while True:
            line = subproc.stdout.readline()
            if line != '':
                print(self.name + '\t' + line.decode('utf-8'))
            try:
                err_line = subproc.stderr.readline()
                if err_line != '':
                    print(self.name + '\t' + err_line.decode('utf-8'))
            except:
                pass
            if subproc.poll() is not None:
                break

        #out, err = subproc.communicate()
        #if stdout != DEVNULL:
        #    print(out.decode('utf-8'))
        #if stderr != DEVNULL and err is not None:
        #    print(err.decode('utf-8'))

    def run(self):
        rate_limit = str(int(128 / self.proc_count))
        for filename in self.package:
            refs_filename = 'refs-' + filename + '.tsv'
            if self.step == 'download':
                self.execute('wget -nc --limit-rate={0}m {1}'.format(rate_limit, self.url_template + filename))
            elif self.step == 'extract':
                self.execute('mwrefs extract {0} > {1}'.format(filename, refs_filename))
                self.execute('rm -f {0}'.format(filename))
            elif self.step == 'ingest':
                self.execute('python3 scan.py {0}'.format(refs_filename))
                self.execute('rm -f {0}'.format(refs_filename))

def bundle_maker(biglist, size):
    """
    Divides a list into smaller lists

    @param biglist: A big list
    @param size: The integer representing how large each sub-list should be
    @return A list of lists that are size `size`
    """

    return [biglist[x:x+size] for x in range(0, len(biglist), size)]

def go(step, proc_count, manifest_file, url_template):
    # https://archive.org/download/enwiki-20170901/enwiki-20170901-pages-meta-history6.xml-p623736p638424.bz2

    manifest = []
    with open(manifest_file) as f:
        reader = csv.reader(f, delimiter='\t')
        for line in reader:
            manifest.append(line[0])

    # Each package in the `packages` is a subqueue for the given process
    # The number of packages should be no greater than the `proc_count`.
    total = len(manifest)
    package_size = int(total / proc_count) + 1
    packages = bundle_maker(manifest, package_size)

    if len(packages) > proc_count:
        raise RuntimeError('More packages than allowed???')

    for package_num, package in enumerate(packages):
        thread = ProcLauncher(
            package_num,
            'thread-' + str(package_num),
            package,
            url_template,
            proc_count,
            step)
        thread.start()
        sleep(1)

if __name__ == '__main__':
    args = sys.argv[1:]
    if len(args) < 4:
        raise RuntimeError
    if args[0] not in ['download', 'extract', 'ingest']:
        raise RuntimeError
    go(args[0], int(args[1]), args[2], args[3])
