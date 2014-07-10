import re

from django.core.management.base import BaseCommand

from speeches.models import Section
from legislature.templatetags.legislature_extras import upper_case_words, heading

# Using a Scrabble word list, which does not contain acronyms, I built lists of
# consonant pairs that do not occur in English words. The prefix and suffix
# pairs exclude the infix pairs to make the regular expressions shorter.
# @see https://code.google.com/p/scrabblehelper/source/browse/trunk/ScrabbleHelper/src/dictionaries/TWL06.txt
prefix_pair = re.compile(r'^(?:bb|bc|bf|bg|bj|bk|bm|bn|bp|bs|bt|bv|bz|cb|cc|cd|ck|cm|cp|cq|cs|db|dc|dd|df|dg|dk|dl|dm|dn|dp|dq|ds|dt|dv|dz|ez|fb|fc|fd|ff|fg|fh|fk|fm|fn|fp|fs|ft|fw|gb|gc|gd|gf|gg|gk|gm|gp|gs|gt|gv|gz|hb|hc|hd|hf|hg|hh|hj|hk|hl|hn|hp|hq|hs|ht|hv|hz|ie|ii|ij|iq|iu|iy|jd|jj|jk|jr|js|kc|kd|kf|kg|kj|kk|km|kp|ks|kt|lb|lc|ld|lf|lg|lh|lj|lk|lm|ln|lp|lq|lr|ls|lt|lv|lx|lz|mc|md|mf|mg|mj|mk|ml|mp|mq|ms|mt|mv|mw|mz|nb|nc|nd|nf|nh|nj|nk|nl|nm|nn|np|nq|nr|ns|nv|nw|nx|nz|oj|pb|pc|pd|pg|pj|pk|pm|pp|pw|qe|qs|rb|rc|rd|rf|rg|rj|rk|rl|rm|rn|rp|rq|rr|rs|rt|rv|rw|rz|sb|sd|ss|sz|tb|td|tf|tg|tj|tk|tl|tn|tp|tq|tt|tv|uc|ue|uj|uo|uq|uu|uw|uy|uz|vd|vg|vk|vl|vn|vs|vv|vz|wb|wc|wd|wf|wg|wj|wk|wl|wm|wn|wp|ws|wt|ww|wz|xb|xc|xd|xf|xg|xh|xl|xm|xn|xo|xp|xq|xs|xt|xv|xw|yb|yd|yf|yg|yh|yj|yk|ym|yn|yr|ys|yv|yx|yy|yz|zb|zc|zd|zg|zh|zj|zk|zm|zn|zp|zq|zs|zt|zv)', re.IGNORECASE)
suffix_pair = re.compile(r'(?:bc|bd|bf|bg|bh|bj|bk|bl|bm|bn|bp|br|bv|bw|bz|cb|cc|cd|cl|cm|cn|cp|cq|cr|cw|cz|db|dc|df|dg|dk|dm|dn|dp|dq|dr|dv|dw|ej|eq|fb|fc|fd|fg|fh|fj|fk|fl|fm|fn|fp|fr|fw|gb|gc|gf|gj|gk|gl|gp|gr|gt|gv|gw|gz|hb|hc|hd|hf|hg|hj|hk|hp|hq|hv|hw|hz|ij|iq|iw|iy|jk|jn|jr|js|kb|kc|kd|kf|kg|kj|kk|kl|km|kn|kp|kr|kt|kv|kw|lg|lh|lj|lq|lr|lv|lw|mc|mg|mh|mj|mk|ml|mq|mr|mv|mw|mz|nb|nf|nj|nl|nm|np|nr|nv|nw|nz|oj|oq|pb|pc|pd|pg|pj|pk|pl|pm|pn|pr|pw|qe|qo|qu|qw|rj|rq|rw|sb|sd|sf|sg|sj|sl|sq|sr|sv|sw|tb|tc|td|tf|tg|tj|tk|tm|tn|tp|tq|tr|tv|tw|uj|vd|vg|vk|vl|vn|vr|vu|vv|vz|wb|wc|wg|wh|wj|wr|wu|ww|wz|xb|xc|xd|xf|xg|xh|xm|xn|xp|xq|xs|xv|xw|yb|yf|yg|yh|yj|yv|yw|yy|yz|zb|zc|zd|zg|zj|zk|zl|zm|zn|zp|zq|zs|zt|zv|zw)$', re.IGNORECASE)
infix_pair = re.compile(r'bq|bx|cf|cg|cj|cv|cx|dx|fq|fv|fx|fz|gq|gx|hx|jb|jc|jf|jg|jh|jl|jm|jp|jq|jt|jv|jw|jx|jy|jz|kq|kx|kz|mx|pq|pv|px|pz|qb|qc|qd|qf|qg|qh|qj|qk|ql|qm|qn|qp|qq|qr|qt|qv|qx|qy|qz|rx|sx|tx|vb|vc|vf|vh|vj|vm|vp|vq|vt|vw|vx|wq|wv|wx|xj|xk|xr|xx|xz|yq|zf|zr|zx', re.IGNORECASE)

# These abbreviations and words are OK.
ignore_words = (
    'No.',
    'Nos.',
    'St.',
    # Honorary prefixes
    'Dr.',
    'Hon.',
    'Mr.',
    'Ms.',
    # Initials
    'D.',
    'F.',
    'G.',
    'J.',
    'K.',
    'L.',
    'P.',
    'W.',
    # Family names
    'McNeil',
    # Months
    'Mar.',
    'Oct.',
    'Nov.',
    'Dec.',
    # Numbers
    '3.5',
)

class Command(BaseCommand):
    help = 'Finds abbreviations in section titles'

    def handle(self, *args, **options):
        for section in Section.objects.all():
            text = heading(section.title)
            test = text[:]
            for word in ignore_words:
                test = test.replace(word, '')
            for word in upper_case_words:
                test = test.replace(word, '')
            if '.' in test or prefix_pair.search(test) or suffix_pair.search(test) or infix_pair.search(test):
                # self.stdout.write('  %s' % section.title)
                self.stdout.write(text)
