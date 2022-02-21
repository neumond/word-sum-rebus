use std::collections::HashMap;

const MAX_WORD: usize = 20;  // 10 ^ 20 max possible fit in u64
const ALPHABET: &str = "абвгдеёжзийклмнопрстуфхцчшщъыьэюя";
const MAX_CHAR: usize = ALPHABET.len();
const MAX_DIGIT: usize = 10;
const EMPTY: u8 = 255;

type CharIndex = u8;
type Digit = u8;

pub struct Converter {
    char_to_index: HashMap<char, CharIndex>,
}

impl Converter {
    fn new() -> Self {
        let mut cti = HashMap::with_capacity(MAX_CHAR);
        for (i, c) in ALPHABET.chars().enumerate() {
            cti.insert(c, i as CharIndex);
        }
        Self { char_to_index: cti }
    }

    fn to_array(&self, s: &str) -> Vec<CharIndex> {
        let slen = s.chars().count();
        let mut r = Vec::with_capacity(slen);
        for ch in s.chars() {
            r.push(self.char_to_index[&ch]);
        }
        r
    }
}

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

pub fn solve(a: &[CharIndex], b: &[CharIndex], s: &[CharIndex]) -> Option<(u64, u64)> {
    // TODO: is this comparison valid?
    if a.len() != b.len() { return None; }
    if ! (s.len() == a.len() || s.len() == a.len() + 1) { return None; }

    let last = a.len() - 1;
    let slast = s.len() - 1;
    let mut pos = 0;
    let mut ans = [EMPTY; MAX_WORD];
    let mut bns = [EMPTY; MAX_WORD];
    let mut sns = [EMPTY; MAX_WORD];
    let mut carry = [0u8; MAX_WORD];
    let mut cmap = CharMap::new();
    if s.len() > a.len() {
        assert!(cmap.try_assign(s[0], 1));
    }
    loop {
        if bns[pos] == EMPTY {
            match cmap.put_or_switch(a[last - pos], ans[pos] == EMPTY) {
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

        match cmap.put_or_switch(b[last - pos], bns[pos] == EMPTY) {
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
        if cmap.try_assign(s[slast - pos], sn10) {
            sns[pos] = sn10;
            carry[pos + 1] = sn / 10;
            pos += 1;
            if pos >= a.len() {
                if (carry[pos] > 0) == (s.len() > a.len()) { break; }
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
    use super::{Converter, solve};

    fn attempt(a: &str, b: &str, s: &str) -> Option<(u64, u64)> {
        let c = Converter::new();
        let aa = c.to_array(a);
        let bb = c.to_array(b);
        let ss = c.to_array(s);
        solve(&aa[..], &bb[..], &ss[..])
    }

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
