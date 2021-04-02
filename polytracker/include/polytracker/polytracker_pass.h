#ifndef POLYTRACKER_INCLUDE_POLYTRACKER_PASS_H_
#define POLYTRACKER_INCLUDE_POLYTRACKER_PASS_H_

#include <vector>
#include "llvm/IR/BasicBlock.h"
#include "llvm/IR/Function.h"
#include "llvm/Pass.h"
#include "llvm/IR/InstVisitor.h"
#include "llvm/IR/DerivedTypes.h"
#include <unordered_map>
#include "llvm/IR/Dominators.h"

namespace polytracker {

typedef uint32_t func_index_t;
typedef uint32_t bb_index_t;

struct PolytrackerPass : public llvm::ModulePass {
  static char ID;
  PolytrackerPass() : ModulePass(ID) {}
  bool runOnModule(llvm::Module &function) override;
  bool analyzeFunction(llvm::Function *f, const func_index_t& index);
  bool analyzeBlock(llvm::Function *func,
                                  const func_index_t& func_index,
                                  llvm::BasicBlock* curr_bb,
                                  const bb_index_t &bb_index,
                                  std::vector<llvm::BasicBlock *> &split_bbs,
                                  llvm::DominatorTree &DT);
  void initializeTypes(llvm::Module &mod);
  void readIgnoreFile(const std::string& ignore_file);
  llvm::Module* mod;
  llvm::FunctionCallee func_entry_log;
  llvm::FunctionType* func_entry_type;
  llvm::FunctionCallee func_exit_log;
  llvm::FunctionCallee bb_entry_log;
  llvm::FunctionCallee taint_op_log;
  llvm::FunctionCallee taint_cmp_log;
  llvm::FunctionCallee dfsan_get_label;

  std::unordered_map<llvm::BasicBlock*, uint64_t> block_global_map;
  std::unordered_map<std::string, func_index_t> func_index_map;
  const int shadow_width = 32;
  llvm::IntegerType *shadow_type;
  std::unordered_map<std::string, bool> ignore_funcs;
};

struct PolyInstVisitor : public llvm::InstVisitor<PolyInstVisitor> {
  void logOp(llvm::Instruction* inst, llvm::FunctionCallee& callback);
  // Visitor instructions
  // Special case for comparisons, just good to know 
  void visitCmpInst(llvm::CmpInst& CI);
  // Handles basically all math operations
  void visitBinaryOperator(llvm::BinaryOperator &I);
  // This is how control flow is handled, we instrument after the call to denote entering a func
  void visitCallInst(llvm::CallInst &ci);

  // TODO Make this reference and on construction
  std::unordered_map<llvm::BasicBlock*, uint64_t> block_global_map;
  std::unordered_map<std::string, func_index_t> func_index_map;
  std::unordered_map<std::string, bool> ignore_funcs;
  llvm::Module* mod;
  llvm::FunctionCallee dfsan_get_label;
  llvm::FunctionCallee taint_op_log;
  llvm::FunctionCallee taint_cmp_log;
  llvm::FunctionCallee func_exit_log;

};

}; // namespace polytracker

#endif /* POLYTRACKER_INCLUDE_POLYTRACKER_PASS_H_ */
