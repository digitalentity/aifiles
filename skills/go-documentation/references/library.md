# Library Documentation

## Public vs Private Libraries

Not all documentation applies equally. Adapt to your audience:

| Documentation | Public Library | Private Library |
| --- | --- | --- |
| Doc comments on exported symbols | Required | Required |
| Package comments | Required | Required |
| README.md | Required | Required |
| Code examples in comments | Generous | Generous |
| `ExampleXxx()` test functions | Recommended | Recommended |
| Go Playground demos | Recommended | N/A (code not public) |
| pkg.go.dev / godoc | Primary docs surface | Use `go doc` locally or internal tooling |
| Documentation website | Large projects | Only if many teams consume the library |
| Register in Context7/DeepWiki/etc. | Recommended | N/A |
| CHANGELOG.md | Recommended | Recommended |
| CONTRIBUTING.md | Recommended | Recommended (internal wiki may suffice) |

**Private libraries** should still have excellent doc comments and examples — teams rotate, people forget, and AI agents need context to help effectively. The main difference is you skip public-facing artifacts (playground, pkg.go.dev, registries).

---

## Example Test Functions

Libraries SHOULD have Example test functions for exported APIs. Example functions are executable documentation. They appear in godoc and are verified by `go test`:

```go
// In map_example_test.go

package mypackage_test

import (
    "fmt"
    "github.com/{owner}/{repo}"
)

// ExampleMap demonstrates mapping over a slice.
func ExampleMap() {
    result := mypackage.Map([]int{1, 2, 3}, func(x int) int {
        return x * 2
    })
    fmt.Println(result)
    // Output: [2 4 6]
}

// ExampleMap_strings demonstrates mapping with string transformation.
func ExampleMap_strings() {
    result := mypackage.Map([]string{"hello", "world"}, strings.ToUpper)
    fmt.Println(result)
    // Output: [HELLO WORLD]
}
```

Naming conventions:

- `ExampleFuncName()` — example for a package-level function
- `ExampleTypeName()` — example for a type
- `ExampleTypeName_MethodName()` — example for a method
- `ExampleFuncName_suffix()` — multiple examples for the same function (suffix is lowercase)
- `Example()` — example for the whole package

The `// Output:` comment MUST be included for `go test` to verify the example. Without it, the example compiles but doesn't verify output.

---

## Code Examples in Doc Comments

Be generous with examples in doc comments. Show common use cases, edge cases, and error handling:

```go
// NewClient creates a new HTTP client with the given options.
//
// Example — basic client:
//
//	client := NewClient()
//
// Example — with custom timeout and retries:
//
//	client := NewClient(
//	    WithTimeout(10 * time.Second),
//	    WithRetries(3),
//	    WithRetryBackoff(time.Second),
//	)
//
// Example — with authentication:
//
//	client := NewClient(
//	    WithBearerToken(os.Getenv("API_TOKEN")),
//	)
func NewClient(opts ...Option) *Client {
```

---

## godoc and pkg.go.dev

Your doc comments automatically render on [pkg.go.dev](https://pkg.go.dev) when you tag a release and someone imports your package. This is the primary documentation surface for public Go libraries.

**How godoc renders comments:**

- First sentence of each doc comment appears in the package index
- `// Package foo provides...` appears as the package description
- Code blocks (indented by one tab) render as formatted code
- `# Heading` syntax (Go 1.19+) creates sections
- `[Link text]` syntax creates hyperlinks
- `[Identifier]` links to other symbols in the package
- `Deprecated:` marker gets special styling

**For private libraries:** pkg.go.dev won't index private modules. Use `go doc` locally or run `pkgsite` on your internal network. Some teams set up a shared pkgsite instance for internal Go modules.

```bash
# View docs for a specific symbol
go doc github.com/{owner}/{repo}.FuncName

# View full package docs
go doc -all github.com/{owner}/{repo}

# Start a local godoc server
go get -tool golang.org/x/pkgsite/cmd/pkgsite@latest
go tool pkgsite -http=:6060
# Then open http://localhost:6060
```

---

## Documentation Website

For larger libraries or frameworks, consider a dedicated documentation website.
