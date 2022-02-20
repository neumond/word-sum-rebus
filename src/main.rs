const MAX_WORD: usize = 20;  // 10 ^ 20 max possible fit in u64
const ALPHABET: &str = "абвгдеёжзийклмнопрстуфхцчшщъыьэюя";
const MAX_DIGIT: usize = 10;
const MAX_CHAR: usize = ALPHABET.len();

type CharIndex = u8;
type Digit = u8;

const EMPTY: u8 = 255;

struct CharMap {
    digit_to_char: [CharIndex; MAX_DIGIT],
    char_to_digit: [Digit; MAX_CHAR],
    ref_counts: [u8; MAX_DIGIT],
}

impl CharMap {
    fn new() -> Self {
        CharMap {
            digit_to_char: [EMPTY; MAX_DIGIT],
            char_to_digit: [EMPTY; MAX_CHAR],
            ref_counts: [0; MAX_DIGIT],
        }
    }

    fn _find_and_set(&mut self, c: CharIndex, frm: u8) -> Option<Digit> {
        let cu = c as usize;
        for i in frm as usize .. MAX_DIGIT {
            if self.digit_to_char[i] == EMPTY {
                self.digit_to_char[i] = c;
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
    loop {
        if bns[pos] == EMPTY {
            match cmap.put_or_switch(aa[pos], ans[pos] == EMPTY) {
                None => {
                    ans[pos] = EMPTY;
                    if pos == 0 { return None; }
                    pos -= 1;
                    cmap.remove(sns[pos]);
                    sns[pos] = EMPTY;
                    carry[pos + 1] = 0;
                    continue;
                },
                Some(an) => {
                    ans[pos] = an;
                },
            }
        }

        match cmap.put_or_switch(bb[pos], bns[pos] == EMPTY) {
            None => {
                bns[pos] = EMPTY;
                continue;
            },
            Some(bn) => {
                bns[pos] = bn;
            },
        }

        let sn = ans[pos] + bns[pos] + carry[pos];
        let sn10 = sn % 10;
        if cmap.try_assign(ss[pos], sn10) {
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
        }
    }

    Some((
        compose_number(&ans[..]),
        compose_number(&bns[..]),
    ))
}

#[cfg(test)]
mod tests {
    use crate::attempt;

    #[test]
    fn solutions() {
        assert_eq!(attempt("деталь", "деталь", "изделие"), Some((684259, 684259)));
        assert_eq!(attempt("удар", "удар", "драка"), Some((8126, 8126)));
        assert_eq!(attempt("один", "один", "много"), Some((6823, 6823)));
        assert_eq!(attempt("вагон", "вагон", "состав"), Some((85679, 85679)));
        assert_eq!(attempt("кис", "кси", "иск"), Some((495, 459)));
    }

    #[test]
    fn no_solution() {
        assert_eq!(attempt("шарик", "мурка", "друзья"), None);
        assert_eq!(attempt("шар", "мир", "пир"), None);
    }

    #[test]
    fn wrong_lengths() {
        assert_eq!(attempt("саша", "маша", "дружба"), None);
        assert_eq!(attempt("солнце", "ветер", "погода"), None);
    }

    // TODO: find multiple solutions
    // ТИК+ТАК=АКТ;
}

fn main() {
    println!("hello");
}
