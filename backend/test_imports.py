try:
    from langchain.chains import RetrievalQA
    print("langchain.chains works")
except Exception as e:
    print(f"langchain.chains fails: {e}")

try:
    from langchain_classic.chains import RetrievalQA
    print("langchain_classic.chains works")
except Exception as e:
    print(f"langchain_classic.chains fails: {e}")

try:
    from langchain_community.chains import RetrievalQA
    print("langchain_community.chains works")
except Exception as e:
    print(f"langchain_community.chains fails: {e}")
