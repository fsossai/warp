import re

with open('app/src/settings_view/custom_inference_modal.rs', 'r') as f:
    content = f.read()

# 1. Remove unused imports at the top
content = re.sub(r'^use std::net\{IpAddr, Ipv4Addr, Ipv6Addr\};\n', '', content, flags=re.MULTILINE)

# 2. Update validate_url
new_validate_url = """fn validate_url(url: &str) -> Result<(), &'static str> {
    if url.trim().is_empty() {
        return Ok(());
    }
    let parsed = Url::parse(url).map_err(|_| "Invalid URL")?;
    if parsed.scheme() != "https" && parsed.scheme() != "http" {
        return Err("URL must use HTTP or HTTPS");
    }
    let Some(_host) = parsed.host_str().filter(|h| !h.is_empty()) else {
        return Err("URL must include a host");
    };
    Ok(())
}"""

# Search strings using triple quotes to avoid issues with single quotes inside the Rust code
search_start = """fn validate_url(url: &str) -> Result<(), &'static str> {"""
search_end = """impl TypedActionView for CustomEndpointModal {"""

start_index = content.find(search_start)
if start_index == -1:
    print("Could not find validate_url")
    exit(1)

end_index = content.find(search_end)
if end_index == -1:
    print("Could not find impl TypedActionView")
    exit(1)

# The block containing all the restriction functions and is_endpoint_form_valid
block_to_replace = content[start_index:end_index]

# Extract is_endpoint_form_valid from the original block
is_endpoint_form_valid_pattern = r'fn is_endpoint_form_valid.*?}'
match = re.search(is_endpoint_form_valid_pattern, block_to_replace, re.DOTALL)
if match:
    is_endpoint_form_valid_func = match.group(0)
    new_block = new_validate_url + '\n\n' + is_endpoint_form_valid_func + '\n\n'
    content = content[:start_index] + new_block + content[end_index:]

with open('app/src/settings_view/custom_inference_modal.rs', 'w') as f:
    f.write(content)
