use std::fs;
use serde_json::{Value, json, to_string_pretty};
use std::fs::write;
use std::env;
fn main() {
    let args: Vec<String> = env::args().collect();
    if args.len() < 2 {
        println!("Please input something like: cargo run <filename.json>");
        std::process::exit(1);
    }
    let filepath = &args[1];
    let data = fs::read_to_string(filepath).expect("Unable to read file");
    let mut json_data: Value = serde_json::from_str(&data).expect("JSON was not well-formatted");
    
    let mut replace_count = 0;
    
    let replace = "add";
    let replaced = "mul";
    
    let instr = json_data["functions"][0]["instrs"].as_array_mut().expect("Instructions should be an array");

    for instruction in instr.iter_mut() {
        if let Some(op) = instruction["op"].as_str() {
            if op == replace {
                instruction["op"] = json!(replaced);
                replace_count += 1;
            }
        }
    }
    
    println!("Replaced {} occurrences of '{}' with '{}'", replace_count, replace, replaced);
    write(filepath.clone() + ".out", to_string_pretty(&json_data).expect("Failed to serialize JSON")).expect("Unable to write file"); 
}
