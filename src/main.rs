const MAX_WORD: usize = 20;
const TENS: [u64; MAX_WORD] = [
    1,
    10,
    100,
    1_000,
    10_000,
    100_000,
    1_000_000,
    10_000_000,
    100_000_000,
    1_000_000_000,
    10_000_000_000,
    100_000_000_000,
    1_000_000_000_000,
    10_000_000_000_000,
    100_000_000_000_000,
    1_000_000_000_000_000,
    10_000_000_000_000_000,
    100_000_000_000_000_000,
    1_000_000_000_000_000_000,
    10_000_000_000_000_000_000,
];
const ALPHABET: &str = "абвгдеёжзийклмнопрстуфхцчшщъыьэюя";
const MAX_DIGIT: u8 = 10;
const MAX_DIGIT_USIZE: usize = MAX_DIGIT as usize;
const MAX_CHAR: u8 = ALPHABET.len() as u8;
const MAX_CHAR_USIZE: usize = MAX_CHAR as usize;

type CharIndex = u8;
type Digit = u8;

const EMPTY: u8 = 255;

struct CharMap {
    digit_to_char: [CharIndex; MAX_DIGIT_USIZE],
    char_to_digit: [Digit; MAX_CHAR_USIZE],
    ref_counts: [u8; MAX_DIGIT_USIZE],
}

impl CharMap {
    fn new() -> Self {
        CharMap {
            digit_to_char: [EMPTY; MAX_DIGIT_USIZE],
            char_to_digit: [EMPTY; MAX_CHAR_USIZE],
            ref_counts: [0; MAX_DIGIT_USIZE],
        }
    }

    fn _find_and_set(&mut self, c: CharIndex, frm: u8) -> Option<Digit> {
        let cu = c as usize;
        for i in frm as usize .. MAX_DIGIT_USIZE {
            if self.digit_to_char[i] == EMPTY {
                self.digit_to_char[i] = c;
                assert!(self.char_to_digit[cu] == EMPTY);
                assert!(self.ref_counts[i] == 0);
                self.char_to_digit[cu] = i as Digit;
                self.ref_counts[i] = 1;
                return Some(i as Digit);
            }
        }
        None
    }

    fn put(&mut self, c: CharIndex) -> Option<Digit> {
        let d = self.char_to_digit[c as usize];
        if d != EMPTY {
            self.ref_counts[d as usize] += 1;
            Some(d)
        } else {
            self._find_and_set(c, 0)
        }
    }

    fn switch(&mut self, c: CharIndex) -> Option<Digit> {
        let d = self.char_to_digit[c as usize];
        assert!(d != EMPTY, "d != EMPTY d={} c={}", d, c);
        if self.remove(d) {
            self._find_and_set(c, d + 1)
        } else {
            None
        }
    }

    fn put_or_switch(&mut self, c: CharIndex, new: bool) -> Option<Digit> {
        if new {
            self.put(c)
        } else {
            self.switch(c)
        }
    }

    fn try_assign(&mut self, c: CharIndex, d: Digit) -> bool {
        let cu = c as usize;
        let du = d as usize;
        if self.digit_to_char[du] != EMPTY || self.char_to_digit[cu] != EMPTY {
            if self.digit_to_char[du] == c {
                self.ref_counts[du] += 1;
                true
            } else {
                false
            }
        } else {
            self.digit_to_char[du] = c;
            self.char_to_digit[cu] = d;
            self.ref_counts[du] = 1;
            true
        }
    }

    fn remove(&mut self, d: Digit) -> bool {
        let du = d as usize;
        if self.ref_counts[du] == 1 {
            let c = self.digit_to_char[du];
            self.digit_to_char[du] = EMPTY;
            self.char_to_digit[c as usize] = EMPTY;
        }
        self.ref_counts[du] -= 1;
        self.ref_counts[du] == 0
    }
}

fn to_char_array(s: &str) -> (usize, [CharIndex; MAX_WORD]) {
    let mut r = [0u8; MAX_WORD];
    let mut sz = 0;
    for (i, c) in s.chars().rev().map(
        |c| ALPHABET.chars().position(|pc| pc == c).unwrap()
    ).enumerate() {
        r[i] = c as u8;
        sz += 1;
    }
    (sz, r)
}

fn compose_number(ds: &[Digit]) -> u64 {
    let mut m = 1;
    let mut r = 0;
    for &d in ds {
        if d == EMPTY { break; }
        r += (d as u64) * m;
        m *= 10;
    }
    r
}

fn attempt(a: &str, b: &str, s: &str) -> Option<(u64, u64)> {
    let (asize, aa) = to_char_array(a);
    let (bsize, bb) = to_char_array(b);
    if asize != bsize { return None; }
    let (ssize, ss) = to_char_array(s);
    if ! (ssize == asize || ssize == asize + 1) { return None; }

    let mut pos = 0;
    let mut ans = [EMPTY; MAX_WORD];
    let mut bns = [EMPTY; MAX_WORD];
    let mut sns = [EMPTY; MAX_WORD];
    let mut carry = [0u8; MAX_WORD];
    let mut cmap = CharMap::new();
    if ssize > asize {
        assert!(cmap.try_assign(ss[ssize - 1], 1));
    }
    let mut iters = 0;
    loop {
        iters += 1;
        eprintln!("====");
        eprintln!("pos={}", pos);
        eprintln!("A={:?}", ans);
        eprintln!("B={:?}", bns);
        eprintln!("S={:?}", sns);
        eprintln!("MAP={:?}", cmap.digit_to_char);
        eprintln!("REF={:?}", cmap.ref_counts);
        eprint!("CHR:");
        cmap.char_to_digit.iter().enumerate().filter(|&(c, d)| *d != EMPTY).for_each(|(c, d)| {
            eprint!(" {}={}", c, d);
        });
        eprintln!("");
        let non_empty_cd = cmap.char_to_digit.iter().filter(|&&d| d != EMPTY).count();
        let non_empty_refs = cmap.ref_counts.iter().filter(|&&c| c > 0).count();
        let non_empty_dc = cmap.digit_to_char.iter().filter(|&&c| c != EMPTY).count();
        eprintln!("{} == {} == {}", non_empty_cd, non_empty_refs, non_empty_dc);

        if bns[pos] == EMPTY {
            assert!(sns[pos] == EMPTY);
            assert!(carry[pos + 1] == 0);
            eprintln!("Switch A");
            match cmap.put_or_switch(aa[pos], ans[pos] == EMPTY) {
                None => {
                    eprintln!("Switch A: Failed");
                    ans[pos] = EMPTY;
                    if pos == 0 { return None; }
                    pos -= 1;
                    assert!(sns[pos] != EMPTY);
                    cmap.remove(sns[pos]);
                    sns[pos] = EMPTY;
                    carry[pos + 1] = 0;
                    continue;
                },
                Some(an) => {
                    eprintln!("Switch A: {}", an);
                    ans[pos] = an;
                },
            }
        }

        eprintln!("Switch B");
        match cmap.put_or_switch(bb[pos], bns[pos] == EMPTY) {
            None => {
                eprintln!("Switch B: Failed");
                bns[pos] = EMPTY;
                assert!(sns[pos] == EMPTY);
                continue;
            },
            Some(bn) => {
                eprintln!("Switch B: {}", bn);
                bns[pos] = bn;
            },
        }

        eprintln!("Attempt S");
        let sn = ans[pos] + bns[pos] + carry[pos];
        let sn10 = sn % 10;
        if cmap.try_assign(ss[pos], sn10) {
            eprintln!("Attempt S: {} + {} = {} ({})", ans[pos], bns[pos], sn10, sn / 10);
            sns[pos] = sn10;
            carry[pos + 1] = sn / 10;
            pos += 1;
            if pos >= asize {
                if (carry[pos] > 0) == (ssize > asize) { break; }
                pos -= 1;
                cmap.remove(sns[pos]);
                sns[pos] = EMPTY;
                carry[pos + 1] = 0;
            }
        } else {
            eprintln!("Attempt S: Failed");
        }
    }

    eprintln!("Iterations {}", iters);

    Some((
        compose_number(&ans[..]),
        compose_number(&bns[..]),
    ))
}

fn main() {
    println!("{:?}", attempt("деталь", "деталь", "изделие"));
}
