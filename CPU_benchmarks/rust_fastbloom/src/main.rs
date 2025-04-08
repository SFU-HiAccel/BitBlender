use std::thread;
use std::sync::{Arc, RwLock};

use fastbloom::BloomFilter;
use std::time::Instant;


const NUM_THREADS: u32 = 24;


fn tmp_testing(num_threads : u32) {
    const EXPECTED_ITEMS: usize = 6*1000*1000;
    const QUERIES_PER_THREAD: u32 = 8*1024*1024;
    let mut filter = BloomFilter::with_false_pos(5e-5 as f64).block_size_512().expected_items(EXPECTED_ITEMS);
    let filter = Arc::new(RwLock::new(filter)); // Shared counter
    let mut handles = vec![];

    // Create threads
    let start = Instant::now();
    for _ in 0..num_threads {
        let filter_clone = Arc::clone(&filter);
        let handle = thread::spawn(move || {
            let filter = filter_clone.read().unwrap();
            for j in 0..QUERIES_PER_THREAD {
                filter.contains( &(j as i32) );
            }
        });
        handles.push(handle);
    }

    for handle in handles {
        handle.join().unwrap(); // Wait for all threads to finish
    }
    let duration = start.elapsed();
    println!("Execution time : {:.6} seconds", duration.as_secs_f64());

    //let handle = thread::spawn(|| {
    //});

    ////let handle = thread::spawn(move || {
    ////});

    //handle.join().unwrap();
}


fn measure_runtime(expected_items: usize, desired_fp_rate: f64) {
    let num_iterations  = 5;
    let num_queries: i32     = 8*1024*1024;
    let mut filter = BloomFilter::with_false_pos(desired_fp_rate).block_size_512().expected_items(expected_items);

    println!("\n\n\nEvaluating a bloom filter with FP={}, expected_num_items={}", desired_fp_rate, expected_items);

    // INSERTIONS
    for i in 0..expected_items {
        let insert_item: i32 = (i as i32) + num_queries;
        filter.insert( &(insert_item) );
    }
    println!("Insertions finished. Testing queries now...");
    println!("This Bloom filter has {} bits over {} blocks, and {} hashes", filter.num_bits(), filter.num_blocks(), filter.num_hashes());


    let filter = Arc::new(RwLock::new(filter)); // To allow multithreaded queries
    let mut handles_1 = vec![];

    // MEMBER QUERIES
    let num_member_iterations = (num_iterations * num_queries) / (expected_items as i32);
    let start = Instant::now();
    for _ in 0..NUM_THREADS {
        let filter_clone = Arc::clone(&filter);
        let handle = thread::spawn(move || {
            let filter = filter_clone.read().unwrap();
            for _ in 0..num_member_iterations {
                for j in 0..expected_items {
                    let member_query: i32 = (j as i32) + num_queries;
                    filter.contains( &(member_query) );
                }
            }
        });
        handles_1.push(handle);
    }

    for handle in handles_1 {
        handle.join().unwrap(); // Wait for all threads to finish
    }
    let duration = start.elapsed();
    println!("Execution time for {} iterations, with {} MEMBER queries: {:.6} seconds", num_member_iterations, expected_items, duration.as_secs_f64());

    // NON-MEMBER QUERIES
    let mut handles_2 = vec![];
    let start = Instant::now();
    for _ in 0..NUM_THREADS {
        let filter_clone = Arc::clone(&filter);
        let handle = thread::spawn(move || {
            let filter = filter_clone.read().unwrap();
            for _ in 0..num_iterations {
                for _ in 0..num_queries {
                    let query = rand::random::<i32>();
                    filter.contains( &(query) );
                }
            }
        });
        handles_2.push(handle);
    }

    for handle in handles_2 {
        handle.join().unwrap(); // Wait for all threads to finish
    }
    let duration = start.elapsed();
    println!("Execution time for {} iterations, with {} NON-MEMBER queries: {:.6} seconds", num_iterations, num_queries, duration.as_secs_f64());
}



fn measure_fp_rate(expected_items: usize,   desired_fp_rate:    f64) {
    let num_queries = 32*1024*1024;
    let mut filter = BloomFilter::with_false_pos(desired_fp_rate).block_size_512().expected_items(expected_items);
    let mut num_false_hits = 0;

    println!("\n\n\nEvaluating FP RATE for a bloom filter with requested FP={}, expected_num_items={}", desired_fp_rate, expected_items);

    // INSERTIONS
    for i in 0..expected_items {
        filter.insert( &(i) );
    }
    println!("Insertions finished. Testing queries now...");
    println!("This Bloom filter has {} bits over {} blocks, and {} hashes", filter.num_bits(), filter.num_blocks(), filter.num_hashes());

    for i in 0..num_queries {
        if filter.contains( &(i+expected_items) ) {
            num_false_hits += 1;
        }
    }
    let experimental_fp_rate = (num_false_hits as f64) / (num_queries as f64);
    println!("Measured: false hits = {:8}, queries = {:8}, FP rate = {:1.10}", num_false_hits, num_queries, experimental_fp_rate);
}





fn main() {
    //println!("Hello, world!");

    //measure_fp_rate(4*1000*1000, 1e-4 as f64);
    //measure_fp_rate(4*1000*1000, 5e-5 as f64);
    //measure_fp_rate(4*1000*1000, 2e-5 as f64);
    //println!("\n-----------------------------------------------\n");

    //measure_fp_rate(6*1000*1000, 1e-4 as f64);
    //measure_fp_rate(6*1000*1000, 5e-5 as f64);
    //measure_fp_rate(6*1000*1000, 2e-5 as f64);
    //println!("\n-----------------------------------------------\n");

    //measure_fp_rate(8*1000*1000, 1e-4 as f64);
    //measure_fp_rate(8*1000*1000, 5e-5 as f64);
    //measure_fp_rate(8*1000*1000, 2e-5 as f64);










    measure_runtime(100*1000, 1e-3 as f64);
    println!("\n-----------------------------------------------\n");

    measure_runtime(4*1000*1000, 1e-4 as f64);
    measure_runtime(4*1000*1000, 5e-5 as f64);
    measure_runtime(4*1000*1000, 2e-5 as f64);
    println!("\n-----------------------------------------------\n");

    measure_runtime(6*1000*1000, 1e-4 as f64);
    measure_runtime(6*1000*1000, 5e-5 as f64);
    measure_runtime(6*1000*1000, 2e-5 as f64);
    println!("\n-----------------------------------------------\n");

    measure_runtime(8*1000*1000, 1e-4 as f64);
    measure_runtime(8*1000*1000, 5e-5 as f64);
    measure_runtime(8*1000*1000, 2e-5 as f64);
}














