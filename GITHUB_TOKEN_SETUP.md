# 🔐 GitHub Token Setup for Automated Workflows

## **Why You Need This**
To automate the workflow triggering from your web page, you need a GitHub Personal Access Token. This allows your website to communicate with GitHub's API.

## **Step 1: Create GitHub Personal Access Token**

1. **Go to GitHub Settings**: [https://github.com/settings/tokens](https://github.com/settings/tokens)
2. **Click "Generate new token"** → **"Generate new token (classic)"**
3. **Fill in the details**:
   - **Note**: "MCQ Generator API Access"
   - **Expiration**: Choose your preferred duration
4. **Select scopes** (permissions):
   - ✅ **repo** (Full control of private repositories)
   - ✅ **workflow** (Update GitHub Action workflows)
5. **Click "Generate token"**
6. **Copy the token** (you won't see it again!)

## **Step 2: Add Token to GitHub Secrets**

1. **Go to your repository**: [https://github.com/rikinptl/quizzer](https://github.com/rikinptl/quizzer)
2. **Click "Settings"** tab
3. **Click "Secrets and variables"** → **"Actions"**
4. **Click "New repository secret"**
5. **Name**: `GITHUB_TOKEN`
6. **Value**: Paste your personal access token
7. **Click "Add secret"**

## **Step 3: Update Your Website**

Replace `YOUR_GITHUB_TOKEN_HERE` in the JavaScript with your actual token, or better yet, use the GitHub Secrets system.

## **Alternative: Use GitHub Secrets in Workflow**

The workflow can access the token via `${{ secrets.GITHUB_TOKEN }}` automatically.

---

## **🚀 Even Better: Serverless Solution**

Instead of using GitHub tokens, let me create a serverless solution using GitHub's webhook system that doesn't require any tokens!
