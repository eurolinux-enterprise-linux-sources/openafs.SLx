#!/bin/sh

# Patch /sbin/weak-modules such that for the openafs.ko module it
# only considers modules as compatible which were built against
# a kernel from the same minor SL release. For example, a module
# built for 2.6.32-71.el6 is compatible with 2.6.32-71.18.1.el6 ,
# but not with 2.6.32-131.5.1.el6.
#
# (C) 2012 Stephan Wiesand <stephan.wiesand@desy.de>
#
#
# The ugly sed command below is equivalent to the following patch:
#
# --- /sbin/weak-modules.orig      2012-12-12 13:37:48.569320952 +0100
# +++ /sbin/weak-modules   2012-12-12 13:47:10.058291022 +0100
# @@ -177,28 +177,38 @@
#      # If the module does not have modversions enabled, $tmpdir/modvers
#      # will be empty.
#      /sbin/modprobe --dump-modversions "$module" \
#      | sed -r -e 's:^(0x[0]*[0-9a-f]{8}\t.*):\1:' \
#      | sort -u \
#      > $tmpdir/modvers
#  
#      # Only include lines of the second file in the output that don't
#      # match lines in the first file. (The default separator is
#      # <space>, so we are matching the whole line.)
#      join -j 1 -v 2 $tmpdir/all-symvers-$krel-$module_krel \
#                     $tmpdir/modvers > $tmpdir/join
# + 
# +    # For openafs: find the X in 2.6.32-X[.y.z].el6 for kernel and module.
# +    declare KREL=${krel#*-}
# +    KREL=${KREL%%.*}
# +    declare MREL=${module_krel#*-}
# +    MREL=${MREL%%.*}
#  
#      if [ ! -s $tmpdir/modvers ]; then
#          echo "Warning: Module ${module##*/} from kernel $module_krel has no" \
#               "modversions, so it cannot be reused for kernel $krel" >&2
# +    elif [ ${module%/openafs.ko} != ${module} -a ${MREL} -ne ${KREL} ]; then
# +        [ -n "$verbose" ] &&
# +        echo "Module ${module##*/} from kernel $module_krel is not compatible" \
# +            "with kernel $krel (different minor SL release)"
#      elif [ -s $tmpdir/join ]; then
#          [ -n "$verbose" ] &&
#          echo "Module ${module##*/} from kernel $module_krel is not compatible" \
#               "with kernel $krel in symbols:" $(sed -e 's:.* ::' $tmpdir/join)
#      else
#          [ -n "$verbose" ] &&
#          echo "Module ${module##*/} from kernel $module_krel is compatible" \
#               "with kernel $krel"
#          return 0
#      fi
#      return 1
#  }

# make sure this is idempotent:
fgrep -q openafs.ko /sbin/weak-modules && exit 0

sed -i -e '/> \$tmpdir\/join/a\ \n    # For openafs: find the X in 2.6.32-X[.y.z].el6 for kernel and module.\n    declare KREL=${krel#*-}\n    KREL=${KREL%%.*}\n    declare MREL=${module_krel#*-}\n    MREL=${MREL%%.*}' \
       -e '/so it cannot be reused/a\    elif [ ${module%/openafs.ko} != ${module} -a ${MREL} -ne ${KREL} ]; then\n        [ -n "$verbose" ] &&\n        echo "Module ${module##*/} from kernel $module_krel is not compatible" \\\n            "with kernel $krel (different minor SL release)"' \
    /sbin/weak-modules

exit 0
