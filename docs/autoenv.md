# Automatic Environment Variables with direnv

## Installation

Install direnv on Ubuntu:

```bash
sudo apt install direnv
```

## Setup for ZSH

Add direnv hook to your ZSH configuration:

```bash
echo 'eval "$(direnv hook zsh)"' >> ~/.zshrc
source ~/.zshrc
```

## Usage

1. **Create `.envrc` file** in your project directory:
   ```bash
   export DATABASE_URL="postgresql://localhost/mydb"
   export API_KEY="your-api-key"
   export DEBUG=true
   export PYTHONPATH="$PWD/src:$PYTHONPATH"
   ```

2. **Allow the directory** (required for security):
   ```bash
   direnv allow
   ```

3. **Test it works**:
   ```bash
   cd /path/to/your/project  # Variables load automatically
   echo $API_KEY             # Should show your value
   cd ..                     # Variables unload automatically
   echo $API_KEY             # Should be empty
   ```

## Security

- direnv requires explicit permission via `direnv allow` before loading any `.envrc` file
- Run `direnv allow` again after modifying `.envrc` files
- Use `direnv deny` to revoke permission for a directory

## Common Commands

```bash
direnv allow     # Allow .envrc in current directory
direnv deny      # Deny .envrc in current directory
direnv reload    # Reload current .envrc
direnv status    # Show current status
```