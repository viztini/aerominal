# aerominal

**aerominal** is an experimental, lightweight fork of the [Kitty](https://github.com/kovidgoyal/kitty) terminal emulator.  
It aims to deliver a minimal, high-performance terminal experience by streamlining the original Kitty codebase and focusing on core functionality.

---

## Project Status

**Current stage:** Early development  
**Alpha releases:** Coming soon

At this stage, **aerominal** is not yet functional or ready for testing.  
The repository currently serves as a staging ground for design decisions, early code experiments, and project planning.

---

## Goals

- Reduce build size and simplify dependencies  
- Improve startup speed and resource efficiency  
- Maintain GPU acceleration and core Kitty features  
- Offer a cleaner and more maintainable codebase  

---

## Planned Features

- Lightweight build with minimal external dependencies  
- Compatibility with Kitty configuration files and themes  
- Optional modules for advanced functionality  
- Simplified code architecture for faster iteration  

---

## Development Roadmap

| Phase | Status | Description |
|--------|---------|-------------|
| Repository setup | ✅ Done | Initial repository and documentation |
| Core code refactor | 🚧 In progress | Stripping down and modularizing Kitty |
| Alpha release | ⏳ Planned | Basic rendering and terminal functionality |
| Feature refinement | ⏳ Planned | Adding config compatibility and optimizations |

---

## Building (Future Instructions)

Once the first alpha release is published, building from source will likely follow a similar process to Kitty:

```bash
git clone https://github.com/viztini/aerominal.git
cd aerominal
make
sudo make install
