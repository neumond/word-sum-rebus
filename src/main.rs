use std::io::Read;
use std::fs::File;
use libflate::gzip::Decoder;

mod solver;
use solver::CharIndex;

fn load_dict(c: &solver::Converter) -> (Vec<CharIndex>, Vec<usize>) {
    let txt = {
        let f = File::open("words.txt.gz").unwrap();
        let mut decoder = Decoder::new(f).unwrap();
        let mut buf = String::new();
        decoder.read_to_string(&mut buf).unwrap();
        buf
    };
    c.to_dict(&txt)
}

type LetterMask = u64;

fn get_letter_mask(w: &[CharIndex]) -> LetterMask {
    let mut r = 0;
    for c in w {
        r |= 1 << c;
    }
    r
}

struct Word {
    ptr: usize,
    len: u8,
    letter_mask: LetterMask,
}

struct IndexedDict {
    chars: Vec<CharIndex>,
    words: Vec<Word>,  // indices in self.chars
    size_shifts: Vec<usize>,  // indices in self.words
}

struct TripletIterator<'a> {
    idc: &'a IndexedDict,
    aidx: usize,
    bidx: usize,
    sidx: usize,
    abmask: LetterMask,
    b_until: usize,
    s_start: usize,
    s_until: usize,
}

impl IndexedDict {
    fn new(chars: Vec<CharIndex>, word_indices: Vec<usize>) -> Self {
        let mut words = Vec::with_capacity(word_indices.len());
        for (i, &ptr) in word_indices.iter().enumerate() {
            let next_p = if i + 1 >= word_indices.len() {
                chars.len()
            } else {
                word_indices[i + 1]
            };
            words.push(Word{
                ptr,
                len: (next_p - ptr) as u8,
                letter_mask: get_letter_mask(&chars[ptr..next_p]),
            });
        }
        words.sort_unstable_by_key(|w| w.len);
        let mut size_shifts = Vec::new();
        for (i, w) in words.iter().enumerate() {
            while w.len as usize >= size_shifts.len() {
                size_shifts.push(i);
            }
        }
        Self { chars, words, size_shifts }
    }

    fn iter_triplets(&self) -> TripletIterator {
        let mut r = TripletIterator {
            idc: &self,
            aidx: 0, bidx: 0, sidx: 0,
            abmask: 0,
            b_until: 0, s_start: 0, s_until: 0,
        };
        let mx = self.words.len();
        let a = *self.size_shifts.get(11).unwrap_or(&mx);
        r._try_set_a(a);
        r
    }
}

impl TripletIterator<'_> {
    fn _try_set_a(&mut self, a: usize) -> bool {
        let total_words = self.idc.words.len();
        if a >= total_words { return false; }
        self.aidx = a;
        // println!("a={}", a);
        let word_len = self.idc.words[self.aidx].len as usize;

        // a + b == b + a
        // no need to check reverse
        self.bidx = self.aidx;

        self.s_start = self.idc.size_shifts[word_len];

        // TODO: uncomment
        // self.b_until = self.aidx + 1;
        self.b_until = *self.idc.size_shifts.get(word_len + 1).unwrap_or(&total_words);

        self.s_until = *self.idc.size_shifts.get(word_len + 2).unwrap_or(&total_words);
        self.sidx = self.s_start;
        // println!("_try_set_a a={} b={} s={}", self.aidx, self.bidx, self.sidx);
        // println!("  s_start={} s_until={} b_until={}", self.s_start, self.s_until, self.b_until);
        true
    }
}

impl<'a> Iterator for TripletIterator<'a> {
    type Item = (&'a [CharIndex], &'a [CharIndex], &'a [CharIndex]);

    fn next(&mut self) -> Option<Self::Item> {
        let sum_word = loop {
            if self.sidx >= self.s_until {
                self.sidx = self.s_start;
                loop {
                    self.bidx += 1;
                    if self.bidx >= self.b_until {
                        if ! self._try_set_a(self.aidx + 1) { return None; }
                    }
                    self.abmask =
                        self.idc.words[self.aidx].letter_mask
                        | self.idc.words[self.bidx].letter_mask;
                    if (self.abmask).count_ones() <= 10 { break; }
                }
            }

            let sum_word = &self.idc.words[self.sidx];
            self.sidx += 1;
            if (sum_word.letter_mask | self.abmask).count_ones() <= 10 {
                break sum_word;
            }
        };

        let a_word = &self.idc.words[self.aidx];
        let b_word = &self.idc.words[self.bidx];
        // eprintln!("a={} b={} s={}", self.aidx, self.bidx, self.sidx - 1);
        assert!(a_word.len == b_word.len);
        assert!((a_word.len ..= a_word.len + 1).contains(&sum_word.len));

        Some((
            &self.idc.chars[a_word.ptr .. a_word.ptr + a_word.len as usize],
            &self.idc.chars[b_word.ptr .. b_word.ptr + b_word.len as usize],
            &self.idc.chars[sum_word.ptr .. sum_word.ptr + sum_word.len as usize],
        ))
    }
}

fn main() {
    let conv = solver::Converter::new();
    let (chars, words) = load_dict(&conv);
    let idc = IndexedDict::new(chars, words);
    // let c = idc.iter_triplets().count();
    // println!("{}", c);
    for (a, b, s) in idc.iter_triplets() {
        match solver::solve(a, b, s) {
            None => {},
            Some((m, k)) => {
                let st_a = conv.to_string(a);
                let st_b = conv.to_string(b);
                let st_s = conv.to_string(s);
                println!("{}+{}={} {}+{}={}", st_a, st_b, st_s, m, k, m + k);
            },
        }
    }
}
